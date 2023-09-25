from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.data_visualization_view, name='data_visualization'),
    path('data_visualization/', views.data_visualization_view, name='data_visualization'),
    path('home/', views.data_visualization_view, name='data_visualization'),
    path('workers/', views.Workers_managment_view, name='workers_managment'),
    path('workers/<int:pk>', views.Workers_managment_edit_view, name='workers_edit'),
    path('login/', views.Login_infra_view, name='login'),
    path('Upload/', views.Upload_view, name='Upload'),
    path('logout/', views.logout_user, name='logout'),
    path('delete_users/', views.delete_users, name='delete_users'),
    path('delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('validation/', views.validation, name='validation'),
    path('print_page/', views.print_page_view, name='print_page'),
    path('pending-files/', views.pending_files, name='pending_files'),
    path('approve-file/<int:file_id>/', views.approve_file, name='approve_file'),
    path('reject-file/<int:file_id>/', views.reject_file, name='reject_file'),
    path('view_uploaded_file/<str:file_name>/', views.view_uploaded_file, name='view_uploaded_file'),
    path('error-500/', views.error_500, name='error_500'),
    path('error-404/', views.error_404, name='error_404'),
    path('download/', views.download_filtered_df_as_excel, name='download_filtered_df_as_excel'),
    path('uploaded-files/', views.view_uploaded_files, name='view_uploaded_files'),
    path('all-users-history/', views.view_all_users_history, name='view_all_users_history'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)