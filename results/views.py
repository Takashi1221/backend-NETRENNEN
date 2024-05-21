from rest_framework import viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta, timezone
from .models import CombinedResults, RaceResults, HorseResults
from .serializers import CombinedResultsSerializer, RaceResultsSerializer, RaceNumberSerializer, HorseEachResultsSerializer

class CombinedResultsViewSet(viewsets.ModelViewSet):
    serializer_class = CombinedResultsSerializer
    def get_queryset(self):
        queryset = CombinedResults.objects.all().order_by('-date')  # 日付で降順に並べ替え
        horse_id = self.request.query_params.get('horse_id')
        if horse_id is not None:
            queryset = queryset.filter(horse_id=horse_id)

        return queryset[:2]
    
    
class RaceResultsViewSet(viewsets.ModelViewSet):
    serializer_class = RaceResultsSerializer
    def get_queryset(self):
        queryset = RaceResults.objects.all()
        race_id = self.request.query_params.get('race_id')
        if race_id is not None:
            queryset = queryset.filter(race_id=race_id)

        return queryset
    
    
# 管理人用レース結果ビュー
@api_view(['GET'])
@authentication_classes([])  # 認証を適用しない
@permission_classes([AllowAny])  # 誰でもアクセスできる
def results_by_date(request):
    date_str = request.query_params.get('date')
    if not date_str:
        return Response({"error": "Date parameter is required"}, status=400)
    
    try:
        # 日付を解析
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
    
    results = RaceResults.objects.filter(date=date)
    serializer = RaceResultsSerializer(results, many=True)
    return Response(serializer.data)


# 管理人用レース結果通過順ポスト
@api_view(['POST'])
@authentication_classes([])  # 認証を適用しない
@permission_classes([AllowAny])  # 誰でもアクセスできる
def submit_passing_order(request):
    data = request.data
    for race_horse_id, details in data.items():
        try:
            result = RaceResults.objects.get(race_horse_id=race_horse_id)
            result.passing_order = details.get('passing_order')
            result.comment = details.get('comment')
            result.save()
        except RaceResults.DoesNotExist:
            continue  # もし該当のレコードが見つからなかった場合はスキップします
    return Response({"message": "通過順の更新が完了しました！"}, status=200)
    
    
class RaceNumberViewSet(viewsets.ModelViewSet):
    serializer_class = RaceNumberSerializer
    def get_queryset(self):
        queryset = RaceResults.objects.all()
        date = self.request.query_params.get('date')
        ort = self.request.query_params.get('ort')

        if date is not None and ort is not None:
            queryset = queryset.filter(date=date, ort=ort)

        return queryset
    
    
class HorseEachResultsiViewSet(viewsets.ModelViewSet):
    serializer_class = HorseEachResultsSerializer
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `horse_id` query parameter in the URL.
        """
        queryset = HorseResults.objects.all()
        horse_id = self.request.query_params.get('horse_id')
        if horse_id is not None:
            queryset = queryset.filter(horse_id=horse_id)
        return queryset