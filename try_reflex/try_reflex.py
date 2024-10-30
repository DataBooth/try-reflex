import reflex as rx
from datetime import datetime

class BlogPost(rx.Model, table=True):
    title: str
    content: str
    created_at: datetime

    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.now()

    
class State(rx.State):
    posts: list[BlogPost] = []
    new_post_title: str = ""
    new_post_content: str = ""

    def add_post(self):
        if self.new_post_title and self.new_post_content:
            with rx.session() as session:
                new_post = BlogPost(title=self.new_post_title, content=self.new_post_content)
                session.add(new_post)
                session.commit()
                session.refresh(new_post)
            self.posts.append(new_post)
            self.new_post_title = ""
            self.new_post_content = ""

    def get_posts(self):
        with rx.session() as session:
            self.posts = session.exec(BlogPost.select().order_by(BlogPost.created_at.desc())).all()

def index():
    return rx.vstack(
        rx.heading("My Blog"),
        rx.input(
            placeholder="Post Title",
            on_change=State.set_new_post_title,
            value=State.new_post_title,
        ),
        rx.text_area(
            placeholder="Post Content",
            on_change=State.set_new_post_content,
            value=State.new_post_content,
        ),
        rx.button("Add Post", on_click=State.add_post),
        rx.divider(),
        rx.foreach(
            State.posts,
            lambda post: rx.vstack(
                rx.heading(post.title, size="md"),
                rx.text(post.content),
                rx.text(f"Created at: {post.created_at.strftime('%Y-%m-%d %H:%M:%S')}"),
                rx.divider(),
                align_items="start",
            ),
        ),
        on_mount=State.get_posts,
        spacing="4",
        width="100%",
        max_width="800px",
        align_items="stretch",
    )

app = rx.App()
app.add_page(index)