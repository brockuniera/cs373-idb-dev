import os
import logging
import re

from whoosh import index, qparser
from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED
from whoosh.qparser import MultifieldParser
from models import Restaurant, Location, Category

whoosh_index_path = "whoosh_index"

def create_whoosh_dir():
    if not os.path.exists(whoosh_index_path):
        os.mkdir(whoosh_index_path)

# Restaurant Schema and Index

class RestaurantSchema(SchemaClass):
    id = ID(stored=True)
    name = TEXT(stored=True)
    phonenum = TEXT(stored=True)
    rating = ID(stored=True)
    reviewcount = ID(stored=True)

def get_restaurant_index():
    if(index.exists_in(whoosh_index_path, indexname="restaurant_index")):
        rest_ix = index.open_dir(whoosh_index_path, indexname="restaurant_index")
    else:
        rest_ix = index.create_in(whoosh_index_path, schema=RestaurantSchema(), 
            indexname="restaurant_index")
        fill_restaurant_index(rest_ix)
    return rest_ix
    
def fill_restaurant_index(ix):
    writer = ix.writer()

    restModelList = Restaurant.query.filter_by().all()
    for restModel in restModelList:
        writer.add_document(name=restModel.name, 
            id=str(restModel.id), 
            phonenum=restModel.phonenum,
            rating=str(restModel.rating),
            reviewcount=str(restModel.reviewcount))
    writer.commit()

# Location Schema and Index

class LocationSchema(SchemaClass):
    id = ID(stored=True)
    address = TEXT(stored=True)
    neighborhood = TEXT(stored=True)
    zipcode = TEXT(stored=True)
    latitude = ID(stored=True)
    longitude = ID(stored=True)

def get_location_index():
    if(index.exists_in(whoosh_index_path, indexname="location_index")):
        loc_ix = index.open_dir(whoosh_index_path, indexname="location_index")
    else:
        loc_ix = index.create_in(whoosh_index_path, schema=LocationSchema(), 
            indexname="location_index")
        fill_location_index(loc_ix)
    return loc_ix
    
def fill_location_index(ix):
    writer = ix.writer()

    locModelList = Location.query.filter_by().all()
    for locModel in locModelList:
        writer.add_document(address=locModel.address, 
            id=str(locModel.id), 
            neighborhood=locModel.neighborhood,
            zipcode=str(locModel.zipcode),
            latitude=str(locModel.latitude),
            longitude=str(locModel.latitude))
    writer.commit()

# Category Schema and Index

class CategorySchema(SchemaClass):
    id = ID(stored=True)
    name = TEXT(stored=True)
    resttotal = ID(stored=True)
    reviewtotal = ID(stored=True)
    ratingavg = ID(stored=True)

def get_category_index():
    if(index.exists_in(whoosh_index_path, indexname="category_index")):
        cat_ix = index.open_dir(whoosh_index_path, indexname="category_index")
    else:
        cat_ix = index.create_in(whoosh_index_path, schema=CategorySchema(), 
            indexname="category_index")
        fill_category_index(cat_ix)
    return cat_ix
    
def fill_category_index(ix):
    writer = ix.writer()
    catModelList = Category.query.filter_by().all()
    for catModel in catModelList:
        writer.add_document(name=catModel.name, 
            id=str(catModel.id), 
            resttotal=str(catModel.resttotal),
            reviewtotal=str(catModel.reviewtotal),
            ratingavg=str(catModel.ratingavg))
    writer.commit()

def search_results(ix, search_query, fields):
    qpo = MultifieldParser(fields, schema=ix.schema, group=qparser.OrGroup)
    qpa = MultifieldParser(fields, schema=ix.schema)
    qo = qpo.parse(search_query)
    qa = qpa.parse(search_query)
    data = []
    data_index = 0

    with ix.searcher() as s:
        resultsa = s.search(qa)
        resultso = s.search(qo)
        for hit in resultsa:
            data.append(dict(**hit))
            context = str()
            for field in fields:
                if(len(hit.highlights(field)) > 0 and hit.highlights(field) not in context):
                    context += re.sub(r"(\(.*[^\)])",r'\1)', hit.highlights(field))
            data[data_index]["context"] = context
            data_index += 1

        for hit in resultso:
            found = False
            for hita in resultsa:
                if hit["id"] == hita["id"]:
                    found = True
            if not found:
                data.append(dict(**hit))
                context = str()
                for field in fields:
                    if(len(hit.highlights(field)) > 0 and hit.highlights(field) not in context):
                        context += re.sub(r"(\(.*[^\)])",r'\1)', hit.highlights(field))
                data[data_index]["context"] = context
                data_index += 1
    return data
