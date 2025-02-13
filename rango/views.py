from django.shortcuts import render
from rango.models import Page
from django.http import HttpResponse
from rango.models import Category
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm
from django.urls import reverse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from django.views import View
from django.utils.decorators import method_decorator
from rango.models import UserProfile
from django.contrib.auth.models import User

def index(request):
    category_list = Category.objects.order_by('-views')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] =  'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['pages'] = page_list
    context_dict['categories'] = category_list  
    
    visitor_cookie_handler(request)
     
    response =  render(request, 'rango/index.html', context=context_dict)
   
    return response

class IndexView(View):
    def get(self,request):
        category_list = Category.objects.order_by('-views')[:5]
        page_list = Page.objects.order_by('-views')[:5]
        context_dict = {
            'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
            'categories': category_list,
            'pages': page_list,
        }
        visitor_cookie_handler(request)
        return render(request, 'rango/index.html', context=context_dict)
    

def about(request):
    print(request.method)
    print(request.user)
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    visitor_cookie_handler(request)
    visits = request.session.get('visits',1)
    context_dict = {
        'visits' : visits,
    }
    
    return render(request, 'rango/about.html', context=context_dict)

class AboutView(View):
    def get(self, request):
        context_dict = {}
        
        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']
        
        return render(request,
                      'rango/about.html',
                      context_dict)


def show_category(request, category_name_slug):
    context_diff = {}
    
    try:
        category = Category.objects.get(slug=category_name_slug)
        
        pages = Page.objects.filter(category=category).order_by("-views")
        
        context_diff['pages'] = pages
        
        context_diff['category'] = category
    except Category.DoesNotExist:
        context_diff['category'] = None
        context_diff['pages'] = None
        
    return render(request, 'rango/category.html', context_diff)


class ShowCategoryView(View):
    def get(self,request, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by("-views")
            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['category'] = None
            context_dict['pages'] = None
        return render(request, 'rango/category.html', context_dict)
@login_required
def add_category(request):
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save(commit=True)
            
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form' : form})

class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})
    
    @method_decorator(login_required)
    def post(self,request):
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    if category is None:
        return redirect(reverse('rango:index'))
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                
                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':
                                                category_name_slug}))
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
    


class AddPageView(View):
    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            return redirect(reverse('rango:index'))
        form = PageForm()
        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            return redirect(reverse('rango:index'))
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()
            return redirect(reverse('rango:show_category',
                                    kwargs={'category_name_slug': category_name_slug }))
        else:
            print(form.errors)
        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)
    
def register(request):
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})
    

class RegisterView(View):
    def get(self, request):
        user_form = UserForm()
        profile_form = UserProfileForm()
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'registered': False
        }
        return render(request, 'registration/registration_form.html', context)
    
    def post(self,request):
        user_form = UserForm(request.POST,)
        profile_form = UserProfileForm(request.POST,request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            
            return redirect(reverse('rango:profile_registration'))
        else:
            print(user_form.errors, profile_form.errors)
            context = {
                'user_form': user_form,
                'profile_form': profile_form,
                'registered': False
            }
            return render(request, 'registration/registration_form.html', context)
            
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')
 
 
 
class UserLoginView(View):
     def get(self, request):
         return render(request, 'rango/login.html')
     
     def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
            

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

class RestrictedView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

class UserLogoutView(View):
    @method_decorator(login_required)
    def get(self, request):
        logout(request)
        return redirect(reverse('rango:index'))

def visitor_cookie_handler(request):
    visits = int(request.session.get('visits', '1'))
    
    last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    
    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits
    

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def goto_url(request):
    page_id = None
    if request.method == 'GET':
        page_id = request.GET.get('page_id')
        
    if page_id:
        try:
            page = Page.objects.get(id=page_id)
            
            page.views += 1
            
            page.save()
            
            return redirect(page.url)
        except Page.DoesNotExist:
            pass
    return redirect(reverse('rango:index'))


class GotoUrlView(View):
    def get(self, request):
        page_id = request.GET.get('page_id')
        if page_id:
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                return redirect(page.url)
            except Page.DoesNotExist:
                pass
        return redirect(reverse('rango:index'))

@login_required
def register_profile(request):
    form = UserProfileForm()
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            
            return redirect('rango:index')
        else:
            print(form.errors)
    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)


class RegisterProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        context_dict  = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('rango:index')
        else:
            print(form.errors)
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)
    


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        userprofile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': userprofile.website,
                                'picture': userprofile.picture})
        return (user, userprofile, form)
    
    @method_decorator(login_required)
    def get(self,request,username):
        
        if request.user.username != username:
            return HttpResponse("You are not allowed to edit this profile.")
        try:
            (user,user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        return render(request, 'rango/profile.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, username):
        if request.user.username != username:
            return HttpResponse("You are not allowed to edit this profile.")
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        
        return render(request, 'rango/profile.html', context_dict)


class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()
        return render(request, 'rango/list_profiles.html', {'user_profile_list': profiles})
    

class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self,request):
        category_id = request.GET['category_id']
        
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1) 
        
        category.likes = category.likes + 1
        category.save()
        
        return HttpResponse(category.likes)
        
          
    

def get_category_list(max_result=0, starts_with='' ):
    category_list = []
    
    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)
        
    if max_result > 0:
        if len(category_list) > max_result:
            category_list = category_list[:max_result]
    return category_list

class CategorySuggestionView(View):
    def get(self,request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''
        category_list = get_category_list(8, suggestion)
        
        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')
        
        return render(request,
                      'rango/categories.html',
                      {'categories': category_list})