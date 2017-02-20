from django.db.models.fields.related import ForeignKey
from django.db.models.fields import CharField, TextField
from django.core.exceptions import FieldDoesNotExist

def update_foreigns(model, key, entities):
    """ 
    根据 entities 数组更新 model 的一对多关系，如果 entity 存在 'id'字段则进行合并，
    否则新建，不存在于 entities 中的会进行删除
    """
    relation = getattr(model, key)
    ids = [e['id'] for e in entities if 'id' in e and e['id']]
    relation.exclude(id__in=ids).delete()
    
    ForeignType = relation.model
    for entity in entities:
        if 'id' in entity and entity['id']:
            foreign = relation.get(id=entity['id'])
            if foreign:
                foreign.merge(entity)
                foreign.save()
        else:
            new = ForeignType.from_dict(entity)
            new.save()
            relation.add(new)


class ConvertMixin:
    @classmethod
    def from_dict(cls, d):
        if d is None: return None
        assert isinstance(d, dict)

        model = cls()
        model.merge(d)
        return model

    @classmethod 
    def default(cls):
        return cls().to_dict()
    
    def to_dict(self, include=[], exclude=[], relation_map=None, include_m2m=True):
        d = {}

        for f in self._meta.concrete_fields:
            if f.name in exclude: continue
            if include and f.name not in include: continue
            if f.is_relation:
                # foreign key
                if relation_map:
                    try:
                        d[f.name] = relation_map(f.name, getattr(self, f.name))
                    except ValueError:
                        pass
                else:
                    d['%s_id' % f.name] = f.value_from_object(self)
            else:
                d[f.name] = f.value_from_object(self)

        if include_m2m:
            for f in self._meta.many_to_many:
                if f.name in exclude: continue
                if include and f.name not in include: continue
                d[f.name] = []
                for i in getattr(self, f.name).all():
                    if relation_map:
                        try:
                            d[f.name].append(relation_map(f.name, i))
                        except ValueError:
                            pass
                    else:
                        d[f.name].append(i.pk)
        try:
            user_field = self._meta.get_field('creator')
            if isinstance(user_field, ForeignKey) and self.creator:
                d['creator'] = self.creator.public_info()
        except FieldDoesNotExist:
            pass
        return d

    def merge(self, d, exclude=[]):
        fields = self._meta.concrete_fields
        for f in fields:
            if f.name in exclude: continue
            if f.name == 'id': continue
            if f.is_relation: continue
            if f.name in d: setattr(self, f.name, d[f.name])
