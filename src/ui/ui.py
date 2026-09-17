from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual.widgets import Footer, Label, ProgressBar
from textual_image.widget import SixelImage
from textual import events
from ui_theme import APP_THEME

IMAGE_NAME = "IMG_GAHSVU21DA"
IMAGE_METADATA = {
    "Type": "Image",
    "Format": "PNG",
    "Category": "Furry",
    "Height": "620",
    "Width": "240",
    "Size": "2.4 MB",
    "Creation date": "21-03-26",
}

CURRENT_INDEX = 14
TOTAL_IMAGES = 258

class ImageViewerApp( App ):
    CSS_PATH = "ui.tcss"
    def compose( self ) -> ComposeResult:
        with Horizontal(classes="stats"):
            with Horizontal(classes="stats-progress"):
                yield Label(f"{CURRENT_INDEX:03d}/{TOTAL_IMAGES:03d}", classes="counter")
                yield ProgressBar( total=TOTAL_IMAGES, show_eta=False, show_percentage=False, classes="progressbar")
        with Horizontal(classes="preview"):
            with VerticalScroll(classes="preview-meta"):
                for label, value in IMAGE_METADATA.items():
                    with Horizontal(classes="meta-row"):
                        yield Label(f"{label}:", classes="meta-label")
                        yield Label(value, classes="meta-value")
            with Container(classes="preview-image"):
                yield SixelImage("TEST_IMAGE.jpg", classes="image")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one_optional('.stats').border_title         = "FURTRATOR"
        self.query_one_optional('.preview-meta').border_title  = IMAGE_NAME
        self.query_one_optional('.preview-image').border_title = "Preview"

        self.register_theme(APP_THEME)  
        self.theme = "APPTHEME"  

if __name__ == "__main__":
    app = ImageViewerApp()
    app.run()