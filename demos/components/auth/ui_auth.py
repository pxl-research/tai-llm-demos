import gradio as gr

from demos.components.auth.fn_auth import add_user, list_all_users, remove_user_on_line

ADMIN_USER = 'admin'  # TODO: change default admin username
ADMIN_PASS = 'cAZgYBF6d4LCn3mQK2hsU5'  # TODO: change default admin password


def on_add_user(username: str, password: str) -> tuple[str | None, str | None, list[list[str]]]:
    current_users = list_all_users()
    if len(username) < 3:
        gr.Warning('Please enter a username of at least 3 characters')
        return username, password, current_users

    if username in current_users:
        gr.Warning('Username is already taken, please choose another one')
        return username, password, current_users

    if len(password) < 10:
        gr.Warning('Please enter a password of at least 10 characters')
        return username, password, current_users

    add_user(username, password)
    gr.Info(f'User "{username}" successfully added!')

    user_list = list_users()
    return None, None, user_list  # clear form, refresh user list


def list_users() -> list[list[str]]:
    user_list = list_all_users()
    df_user_list = []
    for user in user_list:
        df_user_list.append([user])  # wrap in array
    return df_user_list


def on_row_selected(select_data: gr.SelectData) -> int:
    return select_data.index


def on_remove_user(user_list: list[list[str]], select_data: list[int] | None) -> tuple[list[list[str]], None]:
    if select_data is not None:
        user_index = select_data[0]
        user = remove_user_on_line(user_index)
        print('Removed user: ', user)

    user_list = list_users()
    return user_list, None


auth_explainer = (
    'Add a username to the auth file by filling out this form.\n'
    'Make sure you move the file to the correct location after editing!\n')

custom_css = """
    .danger {background: red;}
    .blue {background: #247BA0;}
    footer {display:none !important}
"""

with gr.Blocks(title='User Management', fill_height=True, css=custom_css) as auth_demo:
    st_selected_index = gr.State()

    # UI elements
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            gr.Markdown(auth_explainer)
            tb_username = gr.Textbox(label='Username',
                                     scale=1,
                                     min_width=100,
                                     placeholder='Enter a username of at least 3 characters, e.g. "john"')
            tb_password = gr.Textbox(label='Password',
                                     scale=1,
                                     min_width=100,
                                     placeholder='Enter a password of at least 10 characters',
                                     type="password")
            btn_add = gr.Button(value='Add user',
                                scale=0,
                                min_width=100,
                                elem_classes='blue')

        with gr.Column(scale=1):
            df_users = gr.Dataframe(label='Current users',
                                    scale=1,
                                    min_width=100,
                                    headers=['Username'],
                                    col_count=1,
                                    interactive=False)

            btn_remove_user = gr.Button(value='Remove user',
                                        scale=0,
                                        min_width=100,
                                        elem_classes='danger')

    # events
    btn_add.click(on_add_user, [tb_username, tb_password], [tb_username, tb_password, df_users])
    df_users.select(on_row_selected, None, [st_selected_index])
    btn_remove_user.click(on_remove_user, [df_users, st_selected_index], [df_users, st_selected_index])
    auth_demo.load(list_users, [], [df_users])

auth_demo.launch(auth=(ADMIN_USER, ADMIN_PASS), server_name='0.0.0.0', server_port=7024)
