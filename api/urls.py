from rest_framework_simplejwt.views import TokenRefreshView
from api.views import RegisterView, LoginView, HomeView, RefreshTokenView, LogoutView, CurrentUser, GetCDDUsers, \
    SendPDFEmail, SaveHandover, HandoverList
from django.urls import path

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('me', CurrentUser.as_view(), name='me'),
    path('homepage/', HomeView.as_view(), name='homepage'),
    path('get-cdd-users/', GetCDDUsers.as_view(), name='get-cdd-users'),
    path('send-pdf-email/', SendPDFEmail.as_view(), name='send-pdf-email'),
    path('handover-save/', SaveHandover.as_view(), name='handover-save'),
    path('handover-list/', HandoverList.as_view(), name='handover-list'),
]