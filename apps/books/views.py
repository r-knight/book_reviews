from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from ..users.models import *
from .models import *

def list(request):
    recent = Review.objects.all().order_by('-id')[:3]
    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
    else:
        #ID 0 is a guest account that was created manually
        user = User.objects.get(id=0)
    reviews = Review.objects.all()
    books = Book.objects.filter(id__in=[review.book.id for review in reviews])
    return render(request, 'books/books.html', {'recent': recent, 'user': user, 'books': books})
def destroy(request, review_id):
    if 'id' in request.session:
        review = Review.objects.delete_selected(request.session, review_id)
        if review:
            if 'last_viewed_book' in request.session:
                return redirect('/books/' + str(request.session['last_viewed_book']))
            else:
                return redirect('/books/add')
        else:
            response = "You can't delete another user's reviews!<a href='/books/list'>Back to list</a>"
            return HttpResponse(response)
    else:
        response = "You must be logged in to delete a review!<a href='/books/list'>Back to list</a>"
        return HttpResponse(response)
def view_book(request, book_id):
    if len(Book.objects.filter(id=book_id)) > 0:
        book = Book.objects.get(id=book_id)
        request.session['last_viewed_book'] = book.id
        recent = book.review_set.all().order_by('-id')[:3]
        if 'id' in request.session:
            user = User.objects.get(id=request.session['id'])
        else:
            user = User.objects.get(id=0)
        return render(request, 'books/view_book.html', {'book': book, 'recent': recent, 'user': user})
    else:
        response = "Book with ID " + str(book_id) + "not found.<a href='/books/list'>Back to list</a>"
        return HttpResponse(response)
def add(request):
    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
    else:
        #ID 0 is a guest account that was created manually
        user = User.objects.get(id=0)
    authors = Author.objects.all()
    return render(request, 'books/add.html', {'user': user, 'authors':authors})
def process_book(request):
    if request.method == 'POST':
        errors = Book.objects.basic_validator(request.session, request.POST)
        if len(errors) == 0:
            review = Book.objects.submit_review(request.session)
            if review:
                return redirect('/books/' + str(review.book.id))
            else:
                messages.error(request, "We were unable to submit your review. Please try again.")
                return redirect('/books/add')
        else:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/books/add')
    else:
        response = "This page can only be access with a POST method!<a href='/books/list'>Back to list</a>"
        return HttpResponse(response)
def review_existing(request):
    if request.method == 'POST':
        errors = Book.objects.validate_review_for_existing(request.session, request.POST)
        if len(errors) == 0:
            review = Book.objects.submit_review_for_existing(request.session)
            if review:
                return redirect('/books/' + str(review.book.id))
            else:
                messages.error(request, "We were unable to submit your review. Please try again.")
                if 'last_viewed_book' in request.session:
                    return redirect('/books/'+ str(request.session['last_viewed_book']))
                else:
                    return redirect('/books/add')
        else:
            for key, value in errors.items():
                messages.error(request, value)
            if 'last_viewed_book' in request.session:
                return redirect('/books/'+ str(request.session['last_viewed_book']))
            else:
                return redirect('/books/add')
    else:
        response = "This page can only be access with a POST method!<a href='/books/list'>Back to list</a>"
        return HttpResponse(response)
def edit(request, review_id):
    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
    else:
        #redirect user as guests cannot edit reviews
        messages.error(request, "You must be logged in to edit a review!")
        return redirect('/books/add')
    try:
        review = Review.objects.get(id=int(review_id))
        if review.reviewer.id == user.id:
            request.session['review_id'] = review_id
            return render(request, 'books/edit.html', {'user': user, 'review': review})
        else:
            messages.error(request, "You can only edit your own reviews!")
            return redirect('/books/add')
    except:
        messages.error(request, "Unable to process your edit request. Please try again later.")
        return HttpResponse(response)

def process_edit(request):
    if request.method == 'POST':
        if 'review_id' in request.session:
            errors = Review.objects.edit_validation(request.session, request.POST)
            if len(errors) == 0:
                review = Review.objects.edit_process(request.session)
                if review:
                    return redirect('/books/' + str(review.book.id))
                else:
                    response = "Review not found for review " + str(request.session['review_id'])
                    return redirect('/books/' + str(request.session['review_id']) + '/edit')
            else:
                for key, value in errors.items():
                    messages.error(request, value)
                response = "Placeholder for failed process_edit path for review " + str(request.session['review_id'])
                return redirect('/books/' + str(request.session['review_id']) + '/edit')
        return redirect('/books/add')
    else:
        messages.error(request, "You don't have permission to view that page!")
        return redirect('/books/add')