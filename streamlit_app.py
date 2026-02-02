import streamlit as st
from supabase import create_client, Client
from postgrest.exceptions import APIError

# --- 1. Supabaseの接続設定 ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("Secretsに 'SUPABASE_URL' または 'SUPABASE_KEY' が設定されていません。")
        st.stop()

supabase: Client = init_connection()

st.title("✅ Supabase Todo App")

# --- 2. タスク追加機能 ---
with st.form("add_todo", clear_on_submit=True):
    task = st.text_input("新しいタスクを入力")
    submit = st.form_submit_button("追加")
    
    if submit:
        if task:
            try:
                supabase.table("todos").insert({"task": task}).execute()
                st.success(f"タスクを追加しました: {task}")
                st.rerun()
            except APIError as e:
                st.error(f"追加に失敗しました: {e.message}")
        else:
            st.warning("タスクを入力してください。")

# --- 3. タスク一覧表示と操作 ---
st.subheader("現在のタスク")

try:
    # データの取得
    response = supabase.table("todos").select("*").order("created_at").execute()
    todos = response.data

    if not todos:
        st.info("現在タスクはありません。上のフォームから追加しましょう！")
    else:
        for todo in todos:
            # 完了済みのタスクに打ち消し線を引くためのスタイル設定
            task_text = f"~~{todo['task']}~~" if todo["is_completed"] else todo["task"]
            
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
            
            # A. 完了チェック
            with col1:
                is_done = st.checkbox("", value=todo["is_completed"], key=f"check_{todo['id']}")
                if is_done != todo["is_completed"]:
                    try:
                        supabase.table("todos").update({"is_completed": is_done}).eq("id", todo["id"]).execute()
                        st.rerun()
                    except APIError as e:
                        st.error("更新に失敗しました。")

            # B. タスク名表示
            col2.markdown(task_text)
            
            # C. 削除ボタン
            with col3:
                if st.button("削除", key=f"del_{todo['id']}", type="secondary"):
                    try:
                        supabase.table("todos").delete().eq("id", todo["id"]).execute()
                        st.rerun()
                    except APIError as e:
                        st.error("削除に失敗しました。")

except Exception as e:
    st.error(f"データの読み込み中にエラーが発生しました: {e}")
