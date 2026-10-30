class MediaGroup():
    def __init__(self):
        self.state = "EMPTY"
        self.photos = []
        self.data = {
            "message": "",
            "date": "",
            "images": 0
        }
        self.announcement = False

    def clear(self):
        self.state = "EMPTY"
        self.photos = []
        self.data = {
            "message": "",
            "date": "",
            "images": 0
        }
        self.announcement = False