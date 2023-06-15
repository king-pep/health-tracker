import json
from collections import OrderedDict

import arrow
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, \
    ListAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from entries.fcd import FCD
from entries.models import Entry, Nutrient, Recipe, RecipeIngredient, UserWeight, \
    PhysicalActivity
from entries.permissions import IsOwner, IsNotAnonymous, IsSelf
from entries.serializers import EntrySerializer, NutrientSerializer, \
    RecipeIngredientSerializer, RecipeSerializer, UserSerializer, \
    UserWeightSerializer, PhysicalActivitySerializer


class EntryView(ListCreateAPIView):
    queryset = Entry.objects.all().order_by("-when")
    serializer_class = EntrySerializer
    permission_classes = (IsNotAnonymous,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):

        entry = serializer.save(user=self.request.user)
        data = serializer.initial_data.dict()
        data["extra"] = json.loads(data["extra"])

        if Entry.CATEGORIES.FOOD_CONSUMPTION == entry.category:
            entry.insert_food_nutrients(data["extra"]["ndbno"])
        elif Entry.CATEGORIES.RECIPE_CONSUMPTION == entry.category:
            entry.insert_recipe_nutrients(data["extra"]["recipe_id"])
        elif Entry.CATEGORIES.PHYSICAL_ACTIVITY == entry.category:
            entry.insert_activity_nutrients()
        else:
            raise ValueError("entry type is unknown. {}".format(entry.category))


class NutrientsView(ListAPIView):
    serializer_class = NutrientSerializer
    permission_classes = (IsNotAnonymous,)

    def get_queryset(self):
        entry_id = self.kwargs["entry_id"]
        return Nutrient.objects.filter(
            entry__user=self.request.user,
            entry=entry_id)


class FoodSuggestionView(APIView):
    def get(self, request, frm=None):
        user = request.user
        keyword = request.query_params.get("q").strip()

        recipes = Recipe.objects.filter(user=user, title__contains=keyword)
        recipes = OrderedDict(
            (i.title, {"name": i.title, "id": i.id, "type": "recipe"})
            for i in recipes)

        history = OrderedDict()
        for i in Entry.objects.filter(user=user, what__contains=keyword):
            # if the item is a recipe consumption, then we need to skip it
            # because the recipe's name may be changed or
            # even it might be deleted.
            # besides, recipes will be included as an individual list
            # in the suggestion
            if not i.extra or "recipe_id" in i.get_extra():
                continue

            history[i.what] = {
                "name": i.what,
                "ndbno": json.loads(i.extra).get("ndbno", "")
            }

        try:
            foods = OrderedDict((i["name"], i) for i in FCD.find(keyword))
        except KeyError:
            foods = {}

        # in order to remove duplicates, merge history an recipes with foods.
        # keys occur later in the dicts will overwrite former keys.
        # prioritization: recipes overwrite history, history  overwrites foods
        history.update(foods)
        recipes.update(history)

        # converts to list and then returns
        return Response([i for i in recipes.values()])


class FoodReport(APIView):
    def get(self, request, ndbno, frm=None):
        result = FCD.get_measures(ndbno)
        return Response(result)


class ActivitySuggestionView(APIView):
    def get(self, request, frm=None):
        keyword = request.query_params.get("q").strip()
        records = PhysicalActivity.objects.filter(name__contains=keyword)
        return Response(PhysicalActivitySerializer(records, many=True).data)


class RecipesView(ListCreateAPIView):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsNotAnonymous,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class RecipeView(RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsOwner,)


class RecipeIngredientsView(ListCreateAPIView, DestroyAPIView):
    serializer_class = RecipeIngredientSerializer
    queryset = RecipeIngredient.objects.all()
    permission_classes = (IsNotAnonymous,)

    def get_queryset(self):
        recipe_id = self.kwargs["recipe_id"]
        return RecipeIngredient.objects.filter(
            recipe__user=self.request.user,
            recipe_id=recipe_id)

    def perform_create(self, serializer):
        recipe_id = self.kwargs["recipe_id"]
        # TODO: exception handling
        recipe = Recipe.objects.get(
            user=self.request.user,
            id=recipe_id)
        ingredient = serializer.save(recipe_id=recipe_id)
        ingredient.prepare_nutrients()
        ingredient.save()

        recipe.increase_calorie(ingredient.get_energy())
        recipe.save()

    def perform_destroy(self, ingredient):
        if ingredient.recipe.user != self.request.user:
            raise PermissionDenied()
        ingredient.recipe.decrease_calorie(ingredient.get_energy())
        ingredient.recipe.save()
        super().perform_destroy(ingredient)


class Reports(viewsets.ViewSet):
    permission_classes = (IsNotAnonymous,)

    @classmethod
    def parse_date_range(cls, request):
        """
        parses query params to set start_date and end_date, then returns them
        Args:
            request: Django request object

        Returns:
            (start_date, end_date)
        """
        try:
            start_date = timezone.make_aware(
                arrow.get(request.query_params["start_date"]).naive)
            end_date = timezone.make_aware(
                arrow.get(request.query_params["end_date"]).naive)
            return start_date, end_date
        except MultiValueDictKeyError as e:
            raise KeyError(
                "start_date or/and end_date not found in query params")

    def energy(self, request):
        category = request.query_params["category"]
        start_date, end_date = self.parse_date_range(request)
        report = Nutrient.get_energy_report(
            request.user, category, start_date, end_date)

        return Response({
            "category": category,
            "start_date": start_date,
            "end_date": end_date,
            "label": "Energy",
            "unit": "kcal",
            "data": report
        })

    def weight_history(self, request):
        start_date, end_date = self.parse_date_range(request)
        # Todo: implement actual data and write unit-tests
        data = [
            ["2016-10-01", 74],
            ["2016-10-14", 73.9],
            ["2016-10-23", 72],
            ["2016-11-11", 74],
            ["2016-11-20", 73],
            ["2016-11-23", 74],
            ["2016-12-03", 75]
        ]
        return Response({
            "start_date": start_date,
            "end_date": end_date,
            "data": data
        })

    def consumed_nutrients(self, request):
        start_date, end_date = self.parse_date_range(request)
        report = Nutrient.get_nutrients_report(
            request.user, start_date, end_date)

        return Response({
            "start_date": start_date,
            "end_date": end_date,
            "data": report
        })


class UserWeightsView(ListCreateAPIView):
    serializer_class = UserWeightSerializer
    permission_classes = (IsNotAnonymous,)

    def get_queryset(self):
        try:
            # start_date and end_date filters are optional
            start_date, end_date = Reports.parse_date_range(self.request)
            return UserWeight.objects.filter(
                date__range=[start_date, end_date],
                user=self.request.user).order_by("-date")
        except KeyError as e:
            return UserWeight.objects.filter(
                user=self.request.user).order_by("-date")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class Users(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    used for registration
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelf,)

    def get_me(self, request):
        return Response(self.serializer_class(request.user).data)
