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

        self.color = None
        self.surface = None
        self.size = None

        self.__class__.instances.append(self)
        self.__class__.types.add(self.type)

    @classmethod
    def print_types(c):
        for instance in c.types:
            print(instance)

    @classmethod
    def print_instances(c):
        for instance in c.instances:
            print(instance)