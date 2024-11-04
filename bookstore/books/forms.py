from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'publicationDate': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Book Title',
            'author': 'Author Name',
            'price': 'Book Price',
            'image': 'Book Image',
            'quantity': 'Book Quantity',
            'publicationDate': 'Publication Date',
            'publisher': 'Publisher Name',
            'language': 'Book Language',
            'pages': 'Number of Pages',
        }
        help_texts = {
            'title': 'Enter the title of the book.',
            'author': 'Enter the author of the book.',
            'price': 'Enter the price of the book.',
            'image': 'Upload the image of the book.',
            'quantity': 'Enter the quantity of the book.',
            'publicationDate': 'Enter the publication date of the book.',
            'publisher': 'Enter the publisher of the book.',
            'language': 'Enter the language of the book.',
            'pages': 'Enter the number of pages in the book.',
        }
            

        