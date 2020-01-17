class ObjectInstance(object):

    types = set()
    instances = []

    def __init__(self, obj_id, obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img):

        self.id = obj_id
        self.type = obj_type
        self.confidence = obj_confidence
        self.bounds = obj_bounds
        self.depth = obj_depth
        self.rgb = obj_rgb
        self.img = obj_img

        self.root_path = None
        self.color = None
        self.features = None

        self.__class__.instances.append(self)
        self.__class__.types.add(self.type)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.type, self.id)

    def __unicode__(self):
        return '{} {}'.format(self.color, self.type)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @classmethod
    def print_types(cls):
        for instance in cls.types:
            print(instance)

    @classmethod
    def print_instances(cls):
        for instance in cls.instances:
            print(instance)

    @classmethod
    def data(cls):
        return [instance.features for instance in cls.instances]

    @classmethod
    def all_ids(cls):
        return [instance.id for instance in cls.instances]