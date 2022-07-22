class Topic:

    def __init__(self, id, name, title, description, total_projects_count, avatar_url):
        self.id = id
        self.name = name
        self.title = title
        self.description = description
        self.total_projects_count = total_projects_count
        self.avatar_url = avatar_url

    def __str__(self):
        return f"{self.title}[{self.id}]"

    @staticmethod
    def from_dict(json):
        return Topic(
            id=json['id'],
            name=json['name'],
            title=json['title'],
            description=json['description'],
            total_projects_count=json['total_projects_count'],
            avatar_url=json['avatar_url'],
        )
