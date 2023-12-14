
class Story:
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Story'}
        for key, value in kwargs.items():
            setattr(self, key, value)

class Feature:
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Feature'}
        for key, value in kwargs.items():
            setattr(self, key, value)

class Epic:
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Epic'}
        for key, value in kwargs.items():
            setattr(self, key, value)

# old stuff
# class Story:
#     def __init__(self, summary, description, directie, story_points, role=None, assignee=None):
#         self.issuetype = {'name': 'Story'}
#         self.summary = summary
#         self.description = description
#         self.directie = directie
#         self.story_points = story_points
#         self.labels = []
#         self.tasks = []
#         self.role = role
#         self.assignee = assignee

# class Feature:
#     def __init__(self, summary, description, directie, role=None, assignee=None):
#         self.issuetype = {'name': 'Feature'}
#         self.summary = summary
#         self.description = description
#         self.directie = directie
#         self.labels = []
#         self.stories = []
#         self.role = role
#         self.assignee = assignee

# class Epic:
#     def __init__(self, summary, description, directie):
#         self.issuetype = {'name': 'Epic'}
#         self.summary = summary
#         self.description = description
#         self.directie = directie
#         self.labels = []
#         self.features = []
