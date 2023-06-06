import requests
from bs4 import BeautifulSoup
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import AwardWinner
from .serializers import AwardWinnerSerializer
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny],)
def get_winner(request, pk):
    try:
        winner = AwardWinner.objects.get(pk=pk)
        serializer = AwardWinnerSerializer(winner)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except AwardWinner.DoesNotExist:
        return Response({"error": "Winner not found."}, status=status.HTTP_404_NOT_FOUND)
    
class AwardWinnerViewSet(viewsets.ModelViewSet):
    queryset = AwardWinner.objects.all()
    serializer_class = AwardWinnerSerializer

    def scrape_data(self):
        url = "https://www.forbestravelguide.com/award-winners"
        try:
            driver = webdriver.Chrome()
            WebDriverWait(driver, 60).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            driver.get(url)
            time.sleep(10)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find('table', {'id': 'winnersTable'})  
            directory_rows = table.find('tbody')
            hotels = []
            for row in directory_rows:
                # if count:
                #     print(row)
                property_name = row.find('span', {'class': 'hidden'}).text.strip()
                rating = row.find('span', {'class': 'desktopOnly'}).text.strip()
                hotel = row.find('td', {'class': 'propIconColumn'}).text.strip()
                destination = row.find_all('a')[1].text.strip()
                country = row.find_all('a')[2].text.strip()
                if rating == "Recommended":
                    rating = 5
                else:
                    rating = int(rating[0])
                print(property_name, rating, destination, country, hotel)
                # return Response({"message": "Data scraped successfully."}, status=status.HTTP_200_OK)
                if hotel == "HOTEL":
                    AwardWinner.objects.create(
                        property_name=property_name,
                        rating=rating,
                        destination=destination,
                        country=country
                    )

            return Response({"message": "Data scraped successfully."}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    # # @sync_to_async
    def create(self, request, *args, **kwargs):
        if request.data.get("scrape"):
            return self.scrape_data()
        return super().create(request, *args, **kwargs)
        
    @action(detail=False, methods=['get'])
    def get_scraped_data(self, request):
        queryset = AwardWinner.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
