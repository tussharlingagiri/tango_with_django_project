from django.urls import path
from rango import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

from tango_with_django_project.urls import MyRegistrationView
from .views import(
    IndexView, AboutView, ShowCategoryView,
    AddCategoryView, AddPageView, RegisterView,
    UserLoginView, RestrictedView, GotoUrlView,
    RegisterProfileView , UserLogoutView, ProfileView,
    ListProfilesView, LikeCategoryView, CategorySuggestionView
)

app_name = 'rango'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('about/',AboutView.as_view(), name='about'),
    path('category/<slug:category_name_slug>/',
        ShowCategoryView.as_view(), name= 'show_category'),
    path('add_category/', AddCategoryView.as_view(), name="add_category"),
    path('category/<slug:category_name_slug>/add_page/',AddPageView.as_view(), name='add_page'),
    path('register/', MyRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('restricted/', RestrictedView.as_view(), name='restricted'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('accounts/password/change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('accounts/password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('goto/', GotoUrlView.as_view(), name='goto'),
    path('register_profile/', RegisterProfileView.as_view(), name='profile_registration'),
    path('profile/<username>/', ProfileView.as_view(), name='profile'), 
    path('profiles/',ListProfilesView.as_view(), name='list_profiles'), 
    path('like_category/', LikeCategoryView.as_view(), name='like_category'),
    path('suggest/', CategorySuggestionView.as_view(), name='suggest'),
    
]
