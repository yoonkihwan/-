from repositories.template_repository import TemplateRepository
from models.template import Template

class TemplateService:
    def __init__(self):
        self.repository = TemplateRepository()

    def add_template(self, title, content):
        return self.repository.add_template(title, content)

    def get_all_templates(self):
        templates_data = self.repository.get_all_templates()
        return [Template(id, title, content) for id, title, content in templates_data]
    
    def get_template(self, template_id):
        data = self.repository.get_template(template_id)
        if data:
            return Template(data[0], data[1], data[2])
        return None

    def update_template(self, template_id, title, content):
        return self.repository.update_template(template_id, title, content)

    def delete_template(self, template_id):
        self.repository.delete_template(template_id)
