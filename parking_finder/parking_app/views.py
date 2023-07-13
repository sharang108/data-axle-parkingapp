from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from parking_app.models import Parking, CustomUser
from parking_app.permission import ReadOnly
from parking_app.serializers import ParkingSerializer, UserSerializer
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class UserViewSet(viewsets.ViewSet):
    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=UserSerializer, responses={200: "OK", 400: "Bad Request"}
    )
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class LoginViewSet(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class ParkingPagination(PageNumberPagination):
    page_size = 10


class ParkingViewSet(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
    pagination_class = ParkingPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ReadOnly]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                description="Latitude of the search point",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                description="Longitude of the search point",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "radius",
                openapi.IN_QUERY,
                description="Radius of the search area in meters",
                type=openapi.TYPE_INTEGER,
                default=500,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Token {your_token}",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response("Successful search", ParkingSerializer(many=True)),
            400: "Invalid parameters",
        },
    )
    @action(detail=False, methods=["get"])
    def search(self, request):
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        radius = request.query_params.get("radius", 500)
        if latitude and longitude:
            point = Point(float(longitude), float(latitude))
            queryset = Parking.objects.filter(
                geometry__distance_lte=(point, Distance(m=int(radius)))
            )
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ParkingSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ParkingSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response([])

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user",
                openapi.IN_QUERY,
                description="Filter parking spots reserved by the user",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Token {your_token}",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                "List of reserved parking spots", ParkingSerializer(many=True)
            ),
        },
    )
    @action(detail=False, methods=["get"])
    def reserved(self, request):
        user = request.user
        queryset = Parking.objects.filter(reserved=True, user=user)
        serializer = ParkingSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "parking_id",
                openapi.IN_QUERY,
                description="The ID of the parking spot to reserve",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                description="The ID of the user reserving the parking spot",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Token {your_token}",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response("Successful reservation", ParkingSerializer()),
            400: "Invalid parameters",
        },
    )
    @action(detail=False, methods=["post"])
    def reserve(self, request):
        parking_id = request.query_params.get("parking_id")
        user_id = request.query_params.get("user_id")
        parking = Parking.objects.get(id=parking_id)
        user = CustomUser.objects.get(id=user_id)
        if parking.reserved:
            return Response({"error": "Parking spot already reserved"})
        parking.reserved = True
        parking.user = user
        parking.save()
        serializer = ParkingSerializer(parking)
        return Response(serializer.data)
