import gradio as gr

from demos.components.fn_auth import add_user, list_all_users

ADMIN_USER = 'admin'  # TODO: change default admin username
ADMIN_PASS = 'cAZgYBF6d4LCn3mQK2hsU5'  # TODO: change default admin password


def admin_auth_method(username, password):
    if username == ADMIN_USER and password == ADMIN_PASS:
        return True
    return False


def on_add_user(username, password):
    current_users = list_all_users()
    if len(username) < 3:
        gr.Warning('Please enter a username of at least 3 characters')
        return username, password

    if username in current_users:
        gr.Warning('Username is already taken, please choose another one')
        return username, password

    if len(password) < 10:
        gr.Warning('Please enter a password of at least 10 characters')
        return username, password

    add_user(username, password)
    gr.Info(f'User "{username}" successfully added!')

    return None, None  # clear form


auth_explainer = (
    'Add a username to the auth file by filling out this form.\n'
    'Make sure you move the file to the correct location after editing!\n')

custom_css = """
    .danger {background: red;}
    .blue {background: #247BA0;}
    footer {display:none !important}
"""

with gr.Blocks(title='Add User UI', css=custom_css) as auth_demo:
    # UI elements
    gr.Markdown(auth_explainer)
    tb_username = gr.Textbox(label='Username',
                             min_width=100,
                             placeholder='Enter a username of at least 3 characters, e.g. "john"')
    tb_password = gr.Textbox(label='Password',
                             min_width=100,
                             placeholder='Enter a password of at least 10 characters',
                             type="password")
    btn_add = gr.Button(value='Add user',
                        elem_classes='blue')

    # events
    btn_add.click(on_add_user, [tb_username, tb_password], [tb_username, tb_password])

auth_demo.launch(auth=admin_auth_method, server_name='0.0.0.0', server_port=24024)
