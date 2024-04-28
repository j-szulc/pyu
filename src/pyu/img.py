

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union
    import PIL.Image.Image
    import numpy as np
    from matplotlib.figure import Figure

def resize_image_pil(image_pil, new_width=None, new_height=None):
    assert (new_width is None) != (new_height is None), "Exactly one of new_width or new_height must be specified"
    width, height = image_pil.size
    if new_width is None:
        new_width = int(new_height*width/height)
    if new_height is None:
        new_height = int(new_width*height/width)
    return image_pil.resize((new_width, new_height))

def fig_to_pil(fig: Figure, pad_inches=0.1):
    import io
    import PIL
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", pad_inches=pad_inches, bbox_inches='tight')
    buffer.seek(0)
    result = PIL.Image.open(buffer, formats=["png"])
    return result

def labelled(img: Union[np.array, PIL.Image.Image], text: str, pad_inches=0.1) -> PIL.Image.Image:
    fig = Figure()
    ax = fig.gca()
    ax.imshow(img)
    ax.set_title(text)
    ax.axis("off")
    fig.tight_layout()
    return fig_to_pil(fig, pad_inches=pad_inches)

def make_rowcol(*img: Union[np.array, PIL.ImageImage], axis=1) -> PIL.Image.Image:
    import PIL
    import numpy as np
    return PIL.Image.fromarray(np.concatenate(list(img), axis=axis))
