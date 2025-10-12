






from django.contrib import admin
from .models import CarMake, CarModel

class CarModelInline(admin.TabularInline):
	model = CarModel
	extra = 1

class CarMakeAdmin(admin.ModelAdmin):
	inlines = [CarModelInline]
	list_display = ('name', 'country', 'description')

class CarModelAdmin(admin.ModelAdmin):
	list_display = ('name', 'car_make', 'type', 'year', 'dealer_id', 'color')
	list_filter = ('type', 'year', 'car_make')

admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
