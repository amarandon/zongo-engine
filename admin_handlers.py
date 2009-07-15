#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from UserList import UserList

from google.appengine.ext import db
from base import RequestHandler

class AdminPage(RequestHandler):

    def get(self):
        self.render_to_response("admin/index.html", models=self.models)

class AdminListHandler(RequestHandler):

    def get(self):
        properties = self.model.properties()
        property_labels = [properties[name].verbose_name or name.capitalize() 
                                for name
                                in self.model.visible_properties]
        entities = self.model.get_ordered_list()

        entity_lists = []
        for entity in entities:
            entity_values = UserList()
            for property_name in self.model.visible_properties:
                if hasattr(entity, 'formatted_' + property_name):
                    entity_values.append(getattr(entity,  'formatted_' +
                        property_name))
                else:
                    entity_values.append(getattr(entity, property_name))
            entity_values.id = entity.id
            entity_lists.append(entity_values)

        self.render_to_response('admin/entity_list.html',
                    model=self.model,
                    entities=entity_lists,
                    property_labels=property_labels)


class AdminNewHandler(RequestHandler):

    def get(self):
        self.render_to_response('admin/entity_form.html', 
                form=self.form(), model=self.model, operation='create')

    def post(self):
        data = self.form(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            for name, prop in self.model.properties().items():
                if isinstance(prop, db.BlobProperty):
                    if hasattr(self.request.POST.get(name), 'value'):
                        setattr(entity, name, self.request.POST[name].value)
            entity.put()
            self.redirect("/admin/%ss" % self.name)
        else:
            self.render_to_response('admin/entity_form.html', form=data, model=self.model, 
                    operation='create')


class AdminEditHandler(RequestHandler):

    def get(self, id):
        entity = self.model.get_by_id(int(id))
        self.render_to_response('admin/entity_form.html', 
                form=self.form(instance=entity), model=self.model, operation='update', id=id)

    def post(self, id):
        entity = self.model.get_by_id(int(id))
        assert entity is not None
        data = self.form(data=self.request.POST, instance=entity)
        if data.is_valid():
            entity = data.save(commit=False)
            for name, prop in self.model.properties().items():
                if isinstance(prop, db.BlobProperty):
                    if hasattr(self.request.POST.get(name), 'value'):
                        setattr(entity, name, self.request.POST[name].value)
            entity.put()
            self.redirect("/admin/%ss" % self.name)
        else:
            self.render_to_response('admin/entity_form.html', form=data, model=self.model,
                    operation='update', id=id)


class AdminDeleteHandler(RequestHandler):

    def get(self, id):
        entity = self.model.get_by_id(int(id))
        db.delete(entity)
        self.redirect("/admin/%ss" % self.name)
