from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from .models import Review
from .forms import ReviewForm

# 1. Список рецензій
def reviews_list(request):
    reviews = Review.objects.all()
    return render(request, 'reviews/reviews_list.html', {'reviews': reviews})

# 2. Створення рецензії
@login_required
def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('reviews:reviews_list')
    else:
        form = ReviewForm()
    context = {
        'title': 'Створення рецензії',
        'form': form,
        }    
    return render(request, 'reviews/add_review.html', сontext=context)

class ReviewDetailView(DetailView):
    model = Review
    template_name = 'reviews/review_detail.html'  # Вкажіть правильний шлях до вашого шаблону
    context_object_name = 'review'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review'] = Review.objects.get(pk=self.kwargs['pk'])
        return context
    
# 3. Деталі рецензії
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'reviews/review_detail.html', {'review': review})

# 4. Редагування рецензії
@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user != review.user:
        return redirect('reviews:review_list')  # Тільки власник може редагувати свою рецензію
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('reviews:review_detail', pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/review_form.html', {'form': form})

# 5. Видалення рецензії
@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user == review.user:
        review.delete()
    return redirect('reviews:review_list')

