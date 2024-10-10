from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm

@login_required
def reviews_list(request):
    reviews = Review.objects.filter(user=request.user)
    context = {
        'title': 'List Reviews',
        'reviews': reviews,
    }
    return render(request, 'reviews/reviews_list.html', context)

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
        'title': 'Create a new review',
        'form': form,
        }    
    return render(request, 'reviews/review_create.html', context)


@login_required
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    context = {
        'review': review,
        'title': 'Review detail', 
        
    }
    return render(request, 'reviews/review_detail.html', context)

# 4. Редагування рецензії
@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.user != review.user:
        return redirect('reviews:review_list')  # Тільки власник може редагувати свою рецензію
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('reviews:review_detail', pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    context = {
        'form': form,
        'title': 'Edit review',
        'review': review
        }    

    # Передаємо об'єкт 'review' в контекст разом з формою
    return render(request, 'reviews/review_form.html', context)

# 5. Видалення рецензії
@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user == review.user:
        review.delete()
    return redirect('reviews:reviews_list')

