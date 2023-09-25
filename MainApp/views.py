from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from io import BytesIO
import os
import re
import uuid
from django.utils import timezone
import random
import string
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
from django.conf import settings
from django.shortcuts import render,redirect
from django.http import HttpResponse ,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from matplotlib import pyplot as plt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.models import Session
from MainApp.models import UploadedFile
from collections import defaultdict
from django.utils.datastructures import MultiValueDictKeyError
import openpyxl

# Create your views here.

def download_filtered_df_as_excel(request):

    filename = request.session.get('selected_filename', '')
    session_province = request.session.get('province', '')
    pk_session_data = request.session.get('pk_session_data', {})
    stored_start_range = pk_session_data.get('start_range', '')
    stored_end_renge = pk_session_data.get('end_range', '')
    stored_session_data = request.session.get('session_data', {})
    selected_category = stored_session_data.get('selected_category', '')
    stored_road_filter = stored_session_data.get('road_filter', '')
    # creating my filtred_df
    media_directory = os.path.join(settings.MEDIA_ROOT, '')
    file_path = os.path.join(media_directory, filename)
    df = pd.read_excel(file_path)
    filtered_df = df[df['DPETL'] == session_province]
    filtered_df['Route'] = filtered_df['Categorie'].astype(str) + filtered_df['Num_Route'].astype(str)
    selected_category_int = int(selected_category)
    filtered_df = filtered_df[(filtered_df['Route'] == stored_road_filter) & (filtered_df['voie (sens voie express)'] == selected_category_int)]
    if selected_category_int == 1:
        # Filter the DataFrame based on the range of numbers and category filter
        filtered_df = filtered_df[(filtered_df['pkd'] >= stored_start_range) & (filtered_df['pkf'] <= stored_end_renge)]
    elif int(selected_category) == 2:
        # Filter the DataFrame based on the range of numbers and category filter
        filtered_df = filtered_df[(filtered_df['pkd'] <= stored_start_range) & (filtered_df['pkf'] >= stored_end_renge)]

    # Create an Excel writer object
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    #  writer.book = openpyxl.Workbook()

    # Remove the default sheet created by openpyxl
    #  writer.book.remove(writer.book.active)

    # Convert your DataFrame to an Excel sheet
    filtered_df.to_excel(writer, sheet_name='Filtered_Data', index=False)

    # Save the Excel file to the BytesIO buffer
    writer.save()
    output.seek(0)

    # Create an HTTP response with the Excel file
    filename1 = request.GET.get('filename1', '')
    response = HttpResponse(output.read(), content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename={filename1}.xlsx'

    # Redirect back to the original page
    return response


@login_required(login_url="login")
def data_visualization_view(request):
    '''
    # Fetch list of file names from the media directory
    media_directory = os.path.join(settings.MEDIA_ROOT, '')
    # List all files in the media directory
    files = os.listdir(media_directory)
    
    # Filter only files (excluding directories)
    files = [file for file in files if os.path.isfile(os.path.join(media_directory, file))]
    context1 = {
        'files': files
    }
    '''
    try :
        media_directory = os.path.join(settings.MEDIA_ROOT, '')
        user = request.user  # Get the current user
        files = os.listdir(media_directory)

        # Query the database to get all files with validation_status 'Approved'
        approved_files = UploadedFile.objects.filter(validation_status=UploadedFile.ValidationStatus.APPROVED)

        if user.groups.filter(name='Technicien').exists():
            # If the user is in the "Technician" group, only show their files
            approved_files = approved_files.filter(user=user)

        # Create a list to store approved file names (without paths)
        approved_file_names = []

        # Iterate through the approved files and extract their file names
        for file in approved_files:
            file_name = os.path.basename(file.filename)
            approved_file_names.append(file_name)
        files = [file for file in files if os.path.isfile(os.path.join(media_directory, file))]
        
        
        files_set = set(files)
        approved_files_set = set(approved_file_names)

        # Find the matching filenames
        matching_filenames = files_set.intersection(approved_files_set)

        # Convert the result back to a list if needed
        matching_filenames_list = list(matching_filenames)

        # Include the matching filenames in your context
        context1 = {
            'files': matching_filenames_list,
        }    

        
        
        
        file_name = request.GET.get('selected_filename', '')

        match = re.search(r'RV(\d{4})', file_name)
        # Vérifiez si une correspondance a été trouvée
        if match:
            # Le groupe 1 (le premier groupe capturé) contient les 4 chiffres
            year = match.group(1)

        if file_name and year:
            request.session['selected_filename'] = file_name
            request.session['year'] = year
            file_path = os.path.join(media_directory, file_name)
            # Perform operations on the file (e.g., read data from Excel and process it).
            df = pd.read_excel(file_path)

            # Province
            provinces = df['DPETL'].unique() 
            # Clear the pk_session_data from the session
            if 'province' in request.session:
                del request.session['province']

            if 'pk_session_data' in request.session:
                del request.session['pk_session_data']
            
            if 'session_data' in request.session:
                del request.session['session_data']
            context = {'provinces': provinces}
            messages.success(request, "Fichier séléctionner avec succée !")
            return render(request, 'data_visualization.html', context)
        filename = request.session.get('selected_filename', '')
        year = request.session.get('year', '')
        if filename and year:

            file_path = os.path.join(media_directory, filename)
            # Perform operations on the file (e.g., read data from Excel and process it).
            df = pd.read_excel(file_path)

            # Province
            provinces = df['DPETL'].unique() 
            context = {'provinces': provinces}
            province = request.GET.get('province', '')
            if province:
                request.session['province'] = province
                if 'pk_session_data' in request.session:
                    del request.session['pk_session_data']
                
                if 'session_data' in request.session:
                    del request.session['session_data']
                messages.success(request, "DPETL séléctionner avec succée !")
                return redirect('data_visualization')  # Redirect to the same view
            session_province = request.session.get('province', '')  
            if session_province:
                filtered_df = df[df['DPETL'] == session_province]
            else:
                messages.error(request, "Veuillez choisir un fichier puis la DPETL ...")
                del request.session['selected_filename']
                return redirect('data_visualization')
                
            # Construct the column name based on the selected year
            isu_column_name = f'ISU {str(year)[2:]}'
            # Remove rows with NaN values in the specific column
            filtered_df.dropna(subset=['longueur'], inplace=True)
            #Longueur totale
            longueur_totale = filtered_df['longueur'].sum()
        
            #Longueur RV and largeur moyen
            

            longueur_rv = filtered_df['long rv'].sum()
            larg_moy = filtered_df['Larg_CH'].mean()
            if 'TMJA' in filtered_df.columns :
                tmja_moy = filtered_df['TMJA'].mean()
            else:
                tmja_moy = 0
        
            
            # Combine values from 'column1' and 'column2' and create a new 'combined_column'
            filtered_df['Route'] = filtered_df['Categorie'].astype(str) + filtered_df['Num_Route'].astype(str)

            routes = filtered_df['Route'].unique()

            filtre = False

            # Numero de la route et le sens de la voie
            road_filter = request.GET.get('road', '')
            category = request.GET.get('category_filter', '')
            if road_filter and category:
                session_data = {'selected_category': category, 'road_filter': road_filter}
                request.session['session_data'] = session_data

                if 'pk_session_data' in request.session:
                    del request.session['pk_session_data']

                return redirect('data_visualization')  # Redirect to the same view
        
            stored_session_data = request.session.get('session_data', {})
            selected_category = stored_session_data.get('selected_category', '')
            stored_road_filter = stored_session_data.get('road_filter', '')
            
            if selected_category and selected_category.strip():
                selected_category_int = int(selected_category)
                filtered_df = filtered_df[(filtered_df['Route'] == stored_road_filter) & (filtered_df['voie (sens voie express)'] == selected_category_int)]
                filtre = True
            
                
            pkd_min = filtered_df['pkd'].min()
            pkd_max = filtered_df['pkd'].max()
            pkf_min = filtered_df['pkf'].min()
            pkf_max = filtered_df['pkf'].max()

            start_range_str = request.GET.get('start_range', '')  # Default to empty string if parameter is missing
            end_range_str = request.GET.get('end_range', '')

            # Check if the strings are not empty before converting to float
            if start_range_str:
                start_range = float(start_range_str)
            else:
                start_range = 0.0  # Default value when parameter is missing or empty

            if end_range_str:
                end_range = float(end_range_str)
            else:
                end_range = float('inf')  # Default value when parameter is missing or empty

            filtre1 = False   
            if start_range and end_range:
                pk_session_data = {'start_range': start_range, 'end_range': end_range}
                request.session['pk_session_data'] = pk_session_data
            pk_session_data = request.session.get('pk_session_data', {})
            stored_start_range = pk_session_data.get('start_range', '')
            stored_end_renge = pk_session_data.get('end_range', '')
            if selected_category and selected_category.strip() and stored_start_range and stored_end_renge:
                filtre1 = True
                selected_category_int = int(selected_category)
                if selected_category_int == 1:
                    if stored_start_range < stored_end_renge:
                        # Filter the DataFrame based on the range of numbers and category filter
                        filtered_df = filtered_df[(filtered_df['pkd'] >= stored_start_range) & (filtered_df['pkf'] <= stored_end_renge)]
                    else:
                        messages.error(request, "Le PKD doit être inférieur au PKF pour le sens 1")
                elif int(selected_category) == 2:
                    if stored_start_range > stored_end_renge:
                        # Filter the DataFrame based on the range of numbers and category filter
                        filtered_df = filtered_df[(filtered_df['pkd'] <= stored_start_range) & (filtered_df['pkf'] >= stored_end_renge)]
                    else:
                        messages.error(request, "Le PKD doit être supérieur au PKF pour le sens 2")
            
            # Create a dictionary to store historical data by year and category
            grouped_historical_data = None
            historical_data_by_group = defaultdict(list)

            for index, row in filtered_df.iterrows():
                history = {
                    'pkd': row['pkd'],
                    'pkf': row['pkf'],
                    'hist': row['HIST'],  
                    'revet': row['REVET']
                }
                # Group the historical data by year and category
                key = (row['HIST'], row['REVET'])
                historical_data_by_group[key].append(history)

            if selected_category and selected_category.strip():
                selected_category_int = int(selected_category)
                if selected_category_int == 1:
                    # Convert the grouped historical data into a list of dictionaries
                    grouped_historical_data = [
                        {
                            'hist': key[0],
                            'revet': key[1],
                            'first_pkd': group[0]['pkd'],
                            'last_pkf': group[-1]['pkf']
                        }
                        for key, group in historical_data_by_group.items()
                    ]
                elif int(selected_category) == 2:
                    # Convert the grouped historical data into a list of dictionaries
                    grouped_historical_data = [
                        {
                            'hist': key[0],
                            'revet': key[1],
                            'first_pkd': group[-1]['pkd'],
                            'last_pkf': group[0]['pkf']
                        }
                        for key, group in historical_data_by_group.items()
                    ]
                # filtre appliqué avec succès
                #messages.success(request, 'filtre appliqué avec succès : '+stored_province_filter+'-'+stored_road_filter+'-'+str(selected_category)+'-'+str(stored_start_range)+'-->'+str(stored_end_renge))
                # Check if a similar success message already exists
                success_message = 'filtre appliqué avec succès : '+session_province+'-'+stored_road_filter+'-'+str(selected_category)+'-'+str(stored_start_range)+'-->'+str(stored_end_renge)
                if success_message not in [str(message) for message in messages.get_messages(request)]:
                    messages.success(request, success_message)
                longueur_totale = filtered_df['longueur'].sum()
            
                #Longueur RV and largeur moyen
                longueur_rv = filtered_df['long rv'].sum()
                larg_moy = filtered_df['Larg_CH'].mean()
                if 'TMJA' in filtered_df.columns :
                    tmja_moy = filtered_df['TMJA'].mean()
                else:
                    tmja_moy = 0
                
            # Calculate the count of each category in the filtered DataFrame
            category_counts = filtered_df[isu_column_name].value_counts()
            # Calculate the percentages for each category
            category_percentages = (category_counts / category_counts.sum()) * 100
            # Create a dictionary to hold category labels and corresponding percentages
            category_percentage_data = {
                'A': category_percentages.get('A', 0),
                'B': category_percentages.get('B', 0),
                'S1': category_percentages.get('A', 0)+category_percentages.get('B', 0),
                'C': category_percentages.get('C', 0),
                'D': category_percentages.get('D', 0),
                'S2': category_percentages.get('C', 0)+category_percentages.get('D', 0),
            }
            # Define a dictionary to map categories to colors
            category_color_map = {
                'A': '#3e47e7',
                'B': '#45b116',
                'C': '#eea110',
                'D': '#ff0000'
            }
            # Create a list of colors based on the categories in the DataFrame
            category_colors = [category_color_map[category] for category in category_counts.index]

            # Create a pie chart with percentages
            plt.figure(figsize=(5, 5))
            # Create a list of labels combining color and percentage information
            labels = [f"{category} ({percentage:.1f}%)" for category, percentage in zip(category_counts.index, category_percentages)]

            # Create the pie chart with the updated labels
            plt.pie(category_counts, labels=category_counts.index, startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 1},autopct=lambda p: '{:.1f}%'.format(p) if p > 5 else '', pctdistance=0.8, colors=category_colors)

            
            circle = plt.Circle((0, 0), 0.6, color='white')  # Add a white circle to create the donut effect
            plt.gca().add_artist(circle)
            plt.title('Distribution ISU'+year, loc='left')
            plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
            # Add bounding box to labels to prevent overlaps
            plt.legend(labels=labels, loc="lower left", bbox_to_anchor=(0.9, 0.9))

            # Adjust layout to make space for the legend
            plt.tight_layout()
            # Convert the plot to a base64 encoded image
            buffer = BytesIO()
            plt.savefig(buffer, format='svg') # Save as SVG
            buffer.seek(0)
            plot_svg = buffer.getvalue().decode('utf-8')
            

            
            #Bar Plot
            # Calculate the number of X-axis values
            num_x_values = 0
            if filtered_df['pkf'].any() and filtered_df['pkd'].any():
                num_x_values = int(max(filtered_df['pkf'])) - int(min(filtered_df['pkd'])) + 1

            if filtre is True:
                # Calculate a suitable width based on the number of X-axis values
                max_allowed_width = 65535  # Maximum allowed width
                min_width_per_x_value = 1  # Adjust this value as needed
                min_fig_width = num_x_values * min_width_per_x_value
                fig_width = min(max_allowed_width, max(min_fig_width, 8))  # Set a minimum width of 8 inches

                # Create a figure and axis for the bar plot with the calculated width
                plt.figure(figsize=(fig_width, 5))  # Adjust the height (6 inches) as needed
            else:
                plt.figure(figsize=(8, 5))
            # Create a figure and axis for the bar plot
            ax = plt.gca()
            # Enable grid lines for both X and Y axes
            ax.grid(True, axis='both', linestyle='--', linewidth=0.5, alpha=0.7)
            # Define the order of categories
            category_order = ['A', 'B', 'C', 'D']

            # Calculate a dynamic bar height based on a percentage of the plot height
            bar_height_percentage = 0.2  # Adjust this value as needed
            bar_height = bar_height_percentage * len(category_order)

            # Loop through each category and create a vertical bar for each corresponding row in filtered_df
            for category_index, category in enumerate(category_order):
                category_rows = filtered_df[filtered_df[isu_column_name] == category]
                for index, row in category_rows.iterrows():
                    x_position = row['pkd']
                    bar_width = row['pkf'] - row['pkd']
                    ax.barh(category_index, bar_width, height=bar_height, left=x_position, color=category_color_map.get(category, 'gray'))

            # Set y-axis ticks and labels
            ax.set_yticks(np.arange(len(category_order)))
            ax.set_yticklabels(category_order)
            

            # Set x-axis ticks
            x_ticks = 0
            if filtered_df['pkd'].any() and filtered_df['pkf'].any():
                x_ticks = np.arange(int(min(filtered_df['pkd'])), int(max(filtered_df['pkf'])) + 1)  # Iterate by 1
                ax.set_xticks(x_ticks)

            # Customize the plot
            plt.xlabel('Points kilométriques')
            plt.ylabel('ISU Catégories')
            plt.title('ISU Catégories en fonction des Points kilométriques', loc='left')

            # Invert Y-axis to have A at the top
            plt.gca().invert_yaxis()

            # Show the plot
            plt.tight_layout()
            bar_plot_buffer = BytesIO()
            plt.savefig(bar_plot_buffer, format='svg')
            bar_plot_buffer.seek(0)
            bar_plot_svg = bar_plot_buffer.getvalue().decode('utf-8')
            
            # DataFrame
            
            iac_column_name = f'IAC {str(year)[2:]}'
            
            
            filtered_df = filtered_df.dropna(axis=1, how='all')
            filtered_df = filtered_df.dropna(subset=['DPETL'])
            filtered_df = filtered_df.fillna('-')
            filtered_df = filtered_df.rename(columns={'long rv': 'long_rv', isu_column_name: 'ISU' , 'voie (sens voie express)': 'sens_voie' , iac_column_name: 'IAC'})
            

            context2 = {
                'filtre1': filtre1,
                'filtre': filtre,
                'files': matching_filenames_list,
                'filename': filename,
                'year': year,
                'plot_svg': plot_svg,
                'bar_plot_svg': bar_plot_svg,
                'filtered_df': filtered_df,
                'category_counts': category_counts,
                'category_percentage_data': category_percentage_data,
                'routes': routes,
                'pkd_min': pkd_min,
                'pkd_max': pkd_max,
                'pkf_min': pkf_min,
                'pkf_max': pkf_max,
                'longueur_totale': longueur_totale,
                'longueur_rv': longueur_rv,
                'larg_moy': larg_moy,
                'tmja_moy': tmja_moy,
                'provinces': provinces,
                'selected_province': session_province,  # Add selected province value
                'selected_road': stored_road_filter,          # Add selected road value
                'selected_category': selected_category,       # Add selected category value
                'start_range': stored_start_range,                   # Add start range value
                'end_range': stored_end_renge,                        # Add end range value
                'grouped_historical_data': grouped_historical_data,
                'isu_column_name': isu_column_name,
                'iac_column_name': iac_column_name,
            }
            if 'print_button' in request.POST:
                return render(request, 'print_page.html', context2) 
            
            return render(request, 'data_visualization.html', context2)
            
        return render(request, 'data_visualization.html', context1)
    except Exception as e:
        del request.session['selected_filename']
        messages.error(request,"selected file deleted")
        return render(request, 'data_visualization.html', context1)



@login_required(login_url="login")
def print_page_view(request):

    return render(request,'print_page.html')

@login_required(login_url="login")
@permission_required('MainApp.can_access_employee_management')
def Workers_managment_view(request):
    users = User.objects.all()
    groups = Group.objects.all()
    context = {'groups': groups ,'users':users}
    return render(request,'workers_managment.html',context)
@login_required(login_url="login")

@login_required(login_url="login")
@permission_required('MainApp.can_access_employee_management')
def Workers_managment_edit_view(request, pk):
    user = get_object_or_404(User, id=pk)
    groups = Group.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        new_password = request.POST['password']
        new_group_name = request.POST['role']

        if(new_group_name == "Admin" ):
            is_superuser = True
        else :
            is_superuser = False
                
        # Update user's information
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = is_superuser

        if new_password:
            user.set_password(new_password)  # Update password if provided

        user.save()

        # Remove user from old groups
        user.groups.clear()

        # Add user to the new group if it exists
        if new_group_name:
            try:
                new_group = Group.objects.get(name=new_group_name)
                user.groups.add(new_group)
            except Group.DoesNotExist:
                # Handle the case where the group does not exist
                # You can redirect to an error page or display an error message
                messages.error(request, 'The selected group does not exist.')
        if new_password and username:
            # Send the welcome email
            action_value = 2
            send_welcome_email(request ,username, new_password, email, action_value)

        messages.success(request, 'User data updated successfully.')
        return redirect('workers_managment')

    context = {'user': user, 'groups': groups}
    return render(request, 'workerEdit.html', context)

@login_required(login_url="login")
@permission_required('MainApp.can_access_employee_management')
def delete_users(request):
    if request.method == 'POST':
        user_ids_to_delete = request.GET.get('users', '').split(',')

        # Perform the actual deletion of users
        User.objects.filter(id__in=user_ids_to_delete).delete()

    return redirect('workers_managment')  # Redirect to the workers management page






@login_required(login_url='login')
def approve_file(request, file_id):
    if request.user.groups.filter(name='Admin').exists():
        file = get_object_or_404(UploadedFile, id=file_id)
        file.validation_status  = UploadedFile.ValidationStatus.APPROVED
        file.save()
        messages.success(request, f"File '{file.filename}' has been approved.")
    return redirect('validation')

@login_required(login_url='login')
def reject_file(request, file_id):
    if request.user.groups.filter(name='Admin').exists():
        file = get_object_or_404(UploadedFile, id=file_id)
        file.validation_status  = UploadedFile.ValidationStatus.REJECTED
        file.save()
        messages.success(request, f"File '{file.filename}' has been rejected.")
    return redirect('validation')



@login_required(login_url="login")
@permission_required('MainApp.can_access_validation')
def validation(request):
    if request.user.groups.filter(name='Admin').exists():
        pending_files = UploadedFile.objects.filter(validation_status=UploadedFile.ValidationStatus.PENDING)
        return render(request, 'validation.html', {'pending_files': pending_files})
    else:
        return render(request, 'access_denied.html')
    


@permission_required('MainApp.can_access_employee_management')
def add_employee(request):
    if request.method == 'POST':
        # Extract data from the form
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        role = request.POST['role']  # Assuming 'role' is the name of the <select> element
        is_superuser = False
        if(role == "Admin" ):
            is_superuser = True
        
        # Create the new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser
        )
        
        # Add the user to the selected group
        group = Group.objects.get(name=role)
        user.groups.add(group)
        if password and username:
            # Send the welcome email
            action_value = 1
            send_welcome_email(request ,username, password, email, action_value)
        return redirect('workers_managment')  # Redirect to the workers management page
    
    # If the request method is GET, render the workers_managment.html template
    groups = Group.objects.all()
    context = {'groups': groups}
    return render(request, 'workers_managment.html', context)
@permission_required('MainApp.can_access_employee_management')
def delete_user(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('workers_managment')
    # If the request method is not POST, return a simple response
    return HttpResponse("Method Not Allowed", status=405)



def Login_infra_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        try :
            user = User.objects.get(username = username)
        except:
            messages.error(request, "L'utilisateur n'existe pas !")

        user = authenticate(request,username=username,password=password)
        if user is not None :
            login(request,user)
            if remember_me:  # Check if "Remember Me" is selected
                request.session.set_expiry(60)  # Set session expiration to 2 weeks (in seconds )
            url = reverse('data_visualization')

            return redirect(url)
        else :
            messages.error(request,"Mot de passe incorrect !")
    return render(request,'login_infra.html')






@login_required(login_url="login")
def Upload_view(request):
    if request.method == 'POST':

        try:
            excel_file = request.FILES['excel_file']
            if not excel_file.name.endswith('.xlsx'):
                return render(request, 'Upload.html', messages.error(request, "Seuls les fichiers Excel sont autorisés !!"))
            media_directory = os.path.join(settings.MEDIA_ROOT, '')
            if excel_file is not None:
                # Store the selected file name in the session
                request.session['selected_file_name'] = excel_file.name

            fs = FileSystemStorage(location=media_directory)
            fs.save(excel_file.name, excel_file)
            selected_sheet = request.POST.get('selected_sheet')  # Get the selected sheet name
        except MultiValueDictKeyError:
            return render(request, 'Upload.html', messages.error(request, "le fichier Excel n'a pas été choisi !!"))
        
        # Check if the file name is stored in the session
        if 'selected_file_name' in request.session:
            excel_file_name = request.session['selected_file_name']
            file_path = os.path.join(media_directory, excel_file_name)
            # Read the Excel file without skipping any rows initially
            df = pd.read_excel(file_path, sheet_name=selected_sheet)
            
            # Find the starting row of your actual data table
            start_row = None
            for index, row in df.iterrows():
                # Replace 'Column_Name' with the name of a column that uniquely identifies the start of your data table
                if 'pkf' in row.values:
                    start_row = index
                    break
            
            if start_row is None:
                print("start_row is None")
                # Create a unique filename for the processed Excel file
                processed_file_name = f"{selected_sheet}_{excel_file_name}"

                
                # Remove rows with only underscores or hyphens
                df.replace(['_', '-'], pd.NA, inplace=True)
                df.dropna(how='all', inplace=True)
                df.dropna( axis = 1, how='all', inplace=True)

                # Drop rows with NaN in a certain column (replace 'Column_Name' with the actual column name)
                column_to_check = 'DPETL'
                df.dropna(subset=[column_to_check], inplace=True)

                # Save the processed DataFrame to the media directory
                unique_filename = str(uuid.uuid4()) + "_" + processed_file_name

                processed_file_path = os.path.join(settings.MEDIA_ROOT, unique_filename)
                df.to_excel(processed_file_path, index=False)
                
                
                # Create an instance of the UploadedFile model
                if request.user.groups.filter(name='Technicien').exists():
                    validation_status = UploadedFile.ValidationStatus.PENDING
                else:
                    validation_status = UploadedFile.ValidationStatus.APPROVED

                # Create an instance of the UploadedFile model and save to database
                uploaded_file = UploadedFile(user=request.user, filename=unique_filename, validation_status=validation_status)
                uploaded_file.save()
                messages.success(request, "Le fichier Excel ' " + processed_file_name + " ' a été ajouté avec succès")
                fs.delete(unique_filename)
                return redirect('Upload')
            
            else:
                
                print("start_row is not None")
                # Read the Excel file again, skipping rows before the start_row (including the start_row itself)

                df = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=start_row+1)

                # Remove rows with only underscores or hyphens
                df.replace(['_', '-'], pd.NA, inplace=True)
                df.dropna(how='all', inplace=True)
                df.dropna(axis=1, how='all', inplace=True)

                # Drop rows with NaN in a certain column (replace 'Column_Name' with the actual column name)
                column_to_check = 'DPETL'
                df.dropna(subset=[column_to_check], inplace=True)
                df

                # Process the 'df' DataFrame as needed
                
                # Create a unique filename for the processed Excel file
                processed_file_name = f"{selected_sheet}_{excel_file.name}"
                
                # Save the processed DataFrame to the media directory
                
                unique_filename = str(uuid.uuid4()) + "_" + processed_file_name

                processed_file_path = os.path.join(settings.MEDIA_ROOT, unique_filename)
                df.to_excel(processed_file_path, index=False)
                
                if request.user.groups.filter(name='Technicien').exists():
                    validation_status = UploadedFile.ValidationStatus.PENDING
                else:
                    validation_status = UploadedFile.ValidationStatus.APPROVED

                # Create an instance of the UploadedFile model and save to database
                uploaded_file = UploadedFile(user=request.user, filename=unique_filename, validation_status=validation_status)
                uploaded_file.save()
                # Optionally, you can return the processed_file_path for further use
                # Clear the stored file name from the session
                del request.session['selected_file_name']
                messages.success(request, "Le fichier Excel ' " + processed_file_name + " ' a été ajouté avec succès")
                fs.delete(excel_file_name)
                return redirect('Upload')
                
    return render(request,'Upload.html')


def error_404(request, exception):
    return render(request, 'error.html', {'error_message': 'Page non trouver !'}, status=404)

def error_500(request):
    print("Before clearing session variables:", request.session)
    
    del request.session['selected_filename']
    print("After clearing session variables:", request.session)
    return render(request, 'error.html', {'error_message': 'Erreur de serveur !'}, status=500)

def view_uploaded_file(request, file_name):
    file_path = f"{settings.MEDIA_ROOT}/{file_name}"

    try:
        df = pd.read_excel(file_path)
        headers = df.columns
        data = df.values.tolist()
    except Exception as e:
        headers = []
        data = []
        error_message = f"Error reading the file: {e}"

    context = {
        'headers': headers,
        'data': data,
        'error_message': error_message if 'error_message' in locals() else None,
    }

    return render(request, 'view_uploaded_file.html', context)


@login_required(login_url='login')
def pending_files(request):
    if request.user.groups.filter(name='Technicien').exists():
        pending_files = UploadedFile.objects.filter(user=request.user, validation_status=UploadedFile.ValidationStatus.PENDING)
        return render(request, 'pending_files.html', {'pending_files': pending_files})
    else:
        return render(request, 'access_denied.html')  # Redirect other user groups to an access denied page



def logout_user(request):
    logout(request)
    return redirect("login")
    


@login_required

def view_uploaded_files(request):
    user = request.user  # Get the current user

    # Query the database to get all files uploaded by the user
    uploaded_files = UploadedFile.objects.filter(user=user)

    context = {
        'uploaded_files': uploaded_files,
    }

    return render(request, 'histoy_files.html', context)
@login_required
def view_all_users_history(request):
    # Query the database to get the upload history for all users
    upload_history = UploadedFile.objects.all()

    context = {
        'upload_history': upload_history,
    }

    return render(request, 'all_users_history.html', context)

def send_welcome_email(request ,username, password, recipient_email, action_value):
    user = request.user
    if action_value == 1:
        subject = 'Votre inscription sur le site Infra a été effectuée par M. '+ user.last_name +' '+ user.first_name
    elif action_value == 2:
        subject = 'Des modifications de coordonnées sur votre compte ont été effectuée par M. '+ user.last_name +' '+ user.first_name
    message = f'Nom d\'utilisateur: {username}\nMot de passe: {password}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [recipient_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)