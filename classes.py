class Story:
    def __init__(self, summary, description, directie, story_points):
        self.issuetype = {'name': 'Story'}
        self.summary = summary
        self.description = description
        self.directie = directie
        self.story_points = story_points
        self.tasks = []
        self.assignee = None
        self.parent = None

class Feature:
    def __init__(self, summary, description, directie):
        self.issuetype = {'name': 'Feature'}
        self.summary = summary
        self.description = description
        self.directie = directie
        self.stories = []
        self.assignee = None
        self.parent = None

class Epic:
    def __init__(self, summary, description, directie):
        self.issuetype = {'name': 'Epic'}
        self.summary = summary
        self.description = description
        self.directie = directie
        self.features = []
