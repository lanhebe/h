"""Objects for referencing and de-referencing ids."""

from collections import defaultdict

from h.h_api.enums import DataType
from h.h_api.exceptions import UnpopulatedReferenceError


class IdReferences:
    """A store of id references which can discover and populate them."""

    REF_KEY = "$ref"

    def __init__(self):
        self.id_refs = defaultdict(dict)

    def fill_out_references(self, body):
        """
        Find any references to ids in the data and fill them out.

        We are looking for items like this:

            {"type": <data_type>, "id": {"$ref": <id_ref>}}

        If this matching data is found the object will have the `id` field
        set to the concrete id.

        :raise UnpopulatedReferenceError: When no concrete reference can be found
        """
        for data_type, reference, data_key, data in self._find_references(body):
            data[data_key] = self._get_concrete_id(data_type, reference)

    def add_concrete_id(self, data_type, reference, concrete_id):
        """
        Add a concrete id for a reference.

        :data_type: Data type of the object being referenced
        :reference: The reference string
        :concrete_id: The real id
        """
        data_type = DataType(data_type)

        self.id_refs[data_type][reference] = concrete_id

    def _get_concrete_id(self, data_type, reference):
        data_type = DataType(data_type)
        try:
            return self.id_refs[data_type][reference]
        except KeyError:
            raise UnpopulatedReferenceError(data_type, reference)

    @classmethod
    def _find_references(cls, data):
        """Search for references in the relationships of an object.

        :return: A list of tuples with data type, reference, key and parent
        """

        relationships = data.get("relationships")
        if not relationships:
            return

        for resource_id in relationships.values():
            reference = resource_id["id"].get(cls.REF_KEY)
            if reference is None:
                continue

            yield (DataType(resource_id["type"]), reference, "id", reference)
