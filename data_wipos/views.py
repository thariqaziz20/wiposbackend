from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import DataWiPosSerializer
from .models import DataWiPos
from django.shortcuts import get_object_or_404

"""
second method
"""

class DataWiPosListCreateView(APIView):
    serializer_class = DataWiPosSerializer
    permission_classes =[IsAuthenticated]

    """
    a view for creating and listing data
    """
    def get(self, request:Request, *args, **kwargs):
        posts = DataWiPos.objects.all()
        serializer = self.serializer_class(instance=posts, many=True)
        response = {
                "data" : serializer.data
            }
        return Response(data=response, status=status.HTTP_200_OK)

    def post(self, request : Request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            
            response = {
                "message" : "data",
                "data" : serializer.data
            }

            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



class PostRetrieveUpdateDeleteView(APIView):
    serializer_class = DataWiPosSerializer
    permission_classes =[IsAuthenticated]


    def get(self, requesr : Request, pk:int):
        post = get_object_or_404(DataWiPos, pk=pk)
        serializer = self.serializer_class(instance=post)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request:Request, pk:int):
        post = get_object_or_404(DataWiPos, pk=pk)

        data = request.data
        serializer = self.serializer_class(instance=post,
            data = data                                   
        )
        if serializer.is_valid():
            serializer.save()

            response={
                "message" : "Post Updated",
                "data" : serializer.data
            }

            return Response(data=response, status=status.HTTP_200_OK)
        
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request:Request, pk:int):
        post = get_object_or_404(DataWiPos, pk=pk)

        post.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


"""
fourth method
"""
# class DataWiposViewset(viewsets.ViewSet):
#     def list(self, request:Request):
#         queryset = DataWiPos.objects.all()
#         serializer = DataWiPosSerializer(instance=queryset, many=True)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)
    
#     def retrieve(self, request:Request, pk=None):
#         post=get_object_or_404(DataWiPos, pk=pk)

#         serializer = DataWiPosSerializer(instance=post)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)

"""
third method
"""
# class DataWiPosListCreateView(generics.GenericAPIView,
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin                  
# ):
    
#     serializer_class = DataWiPosSerializer
#     permission_classes = [IsAuthenticated]
#     queryset=DataWiPos.objects.all()

#     def get(self, request:Request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request:Request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


# class DataWiPosRetrieveUpdateDeleteView(generics.GenericAPIView,
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     mixins.DestroyModelMixin                  
# ):
#     serializer_class = DataWiPosSerializer
#     queryset=DataWiPos.objects.all()

#     def get(self, request:Request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def put(self, request:Request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
    
#     def delete(self, request:Request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)




"""     
first method
"""

# @api_view(['GET'])
# def getAllDataWiPos(request):
#     notes = DataWiPos.objects.all()
#     serializer = DataWiPosSerializer(notes, many=True)
#     response = {
#         "data" : serializer.data
#     }
#     return Response(response)

# @api_view(['GET'])
# def getDataWiPos(request, pk):
#     note = DataWiPos.objects.get(id=pk)
#     serializer = DataWiPosSerializer(note, many=False)
#     response = {
#         "data" : serializer.data
#     }
#     return Response(response)


# @api_view(['POST'])
# def createDataWiPos(request):
#     data = request.data

#     note = DataWiPos.objects.create(
#         username = data['username'],
#         lokasi = data['lokasi'],
#         ssid = data['ssid'],
#         macaddress = data['macaddress'],
#         rssi = data['rssi']
#     )
#     serializer = DataWiPosSerializer(note, many=False)

#     response = {
#         "data" : serializer.data
#     }
#     return Response(response)


# @api_view(['PUT'])
# def updateDataWiPos(request, pk):
#     data = request.data

#     note = DataWiPos.objects.get(id=pk)
#     serializer = DataWiPosSerializer(note, data=request.data)
#     if serializer.is_valid():
#         serializer.save()

#     response = {
#         "data" : serializer.data
#     }
#     return Response(response)


# @api_view(['DELETE'])
# def deleteDataWiPos(request, pk):
#     note = DataWiPos.objects.get(id=pk)
#     note.delete()
#     return Response('Data WiPos Was Deleted')