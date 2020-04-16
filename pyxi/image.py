import json
import zipfile
from typing import Any, Dict, List, Union

import PIL
from PIL import Image

from pyxi.animation import Animation
from pyxi.canvas import Canvas
from pyxi.palette import Palette
from pyxi.tileset import Tileset


class PyxelImage:
    __slots__ = ('_path', 'version', 'name', 'settings', 'canvas', 'palette', 'tileset', 'animations')

    def __init__(self, file: str):
        super().__init__()
        data = self._get_data_ref(file)
        self._path = file
        self.version = data['version']
        self.name = data['name']
        self.settings = {}
        self.canvas = Canvas(data['canvas'])
        self.palette = Palette(data['palette'])
        self.tileset = Tileset(data['tileset'])
        self.animations = {n: Animation(n, data['animations'][str(n)]) for n in range(len(data['animations']))}

    def get_tile(self) -> PIL.Image.Image:
        """Merges layers and returns the image.

        :returns: New :py:class:`PIL.Image.Image` object."""
        img = self.merge_layers()
        return img

    def merge_layers(self, skip_layers: List[Union[str, int]] = None, base_layer: int = 0) -> PIL.Image.Image:
        """Merges layer images onto the defined base layer and returns the new Image object.

        :param skip_layers: Not implemented.
        :param int base_layer: Changes the base layer to merge on.
        :returns: New :py:class:`PIL.Image.Image` object.
        """

        if skip_layers is None:
            skip_layers = []

        with zipfile.ZipFile(self._path, 'r') as f:
            base = Image.open(f.open(f'layer{base_layer}.png'))

            if base_layer != 0:
                remaining_layers = [layer.layer_id for layer in self.canvas.layers if layer != base_layer]

            for layer_id in remaining_layers:
                if layer_id not in skip_layers:
                    next_layer = Image.open(f.open(f'layer{layer_id}.png'))
                    base.paste(next_layer, (0, 0), next_layer.convert('RGBA'))

            return base

    def extract(self):
        """Extracts all the individual files from a .pyxel file and
        places them in a converted/<file_name> directory."""
        with zipfile.ZipFile(self._path, 'r') as f:
            f.extractall(f'converted/{self.name}')

    @staticmethod
    def _get_data_ref(file: str) -> Dict[str, Any]:
        """Gets the .pyxel JSON data reference for mapping to the PyxelImage
        object. Internal use only.

        :param str file: String pointing to the .pyxel file you are opening.
        :returns: JSON-mapped dictionary.
        """

        with zipfile.ZipFile(file, 'r') as f:
            doc_file = f.read('docData.json')
            return json.loads(doc_file)
