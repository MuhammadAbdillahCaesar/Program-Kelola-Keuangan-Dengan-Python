import streamlit as st
import pyrebase
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
import base64
import plotly.express as px
from datetime import datetime
import os
from xlsxwriter import Workbook

firebaseConfig = {
    "apiKey": "AIzaSyBzKpCid35jH7MZEVhec8vb0cGQ4j3sS_Q",
    "authDomain": "your-app.firebaseapp.com",
    "databaseURL": "https://your-app.firebaseio.com",
    "projectId": "your-app",
    "storageBucket": "your-app.appspot.com",
    "messagingSenderId": "your-messaging-sender-id",
    "appId": "your-app-id",
    "measurementId": "your-measurement-id"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

#function daftar
def sign_up(email, password):
    try:
        if not email or not email.strip():
            return "Email address is required."

        if not password or not password.strip():
            return "Password is required."

        user = auth.create_user_with_email_and_password(email, password)
        
        auth.send_email_verification(user['idToken'])

        return None
    except Exception as e:
        return str(e)
    
#function masuk
def login(email, password):
    try:
        if not email or not email.strip():
            return "Email salah."

        if not password or not password.strip():
            return "Password salah."

        login = auth.sign_in_with_email_and_password(email, password)

        user = auth.get_account_info(login['idToken'])
        if user['users'][0]['emailVerified']:
            return None  
        else:
            return "Email tidak terverifikasi. Cek email anda"
    except Exception as e:
        if "INVALID_LOGIN_CREDENTIALS" in str(e):
            return "Akun tidak ada."
        
#function reset
def reset_password(email):
    try:
        if not email or not email.strip():
            return "Email address is required."

        auth.send_password_reset_email(email)
        return None  
    except Exception as e:
        return str(e)

#function delete
def delete_account(email, password):
    try:
        if not email or not email.strip():
            return "Email address is required."

        if not password or not password.strip():
            return "Password is required."

        user = auth.sign_in_with_email_and_password(email, password)

        auth.delete_user_account(user['idToken'])
    except Exception as e:
        return "Account has been deleted."

#function image base64   
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#function download file(perhitungan keungan)
def download_file(excel_path, excel_name):
    with open(excel_path, 'rb') as f:
        excel_data = f.read()
    b64 = base64.b64encode(excel_data).decode('utf-8')
    file_name = excel_name
    href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'

    button_style = """
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    """

    st.markdown(
        f'<a href="{href}" download="{file_name}" style="{button_style}">Download Data</a>',
        unsafe_allow_html=True
    )
            
class BaseKeuanganApp:
        def __init__(self):
            self.income_transactions = []
            self.expense_transactions = []
            self.future_value = []

class GuiView(BaseKeuanganApp):
    if not st.session_state.get('is_logged_in'):
        #wallpapper
        img = get_img_as_base64("C:\\Users\\MAbdi\\OneDrive\\Dokumen\\Finish\\login.png")
        Walpaper = f"""
                        <style>
                        [data-testid="stAppViewContainer"] > .main {{
                        background-image: url("data:image/png;base64,{img}");
                        background-size: cover;
                        background-position: top left;
                        background-repeat: repeat;
                        backgroung-attachment: fixed;
                        }}
                        </style>
                        """
        st.markdown(Walpaper, unsafe_allow_html=True)
        #sidebar akun
        with st.sidebar:
            selected_action = option_menu(
                menu_title="Akun",
                options=["Daftar", "Masuk", "Reset Password", "Hapus Akun"],
                icons=["arrow-bar-up","door-open","arrow-repeat","trash3"],
                menu_icon='list',
                default_index=0,
            )

        #Pengondisian halaman akun
        if selected_action == "Daftar":
            st.title('Daftar Akun')
            email = st.text_input("Masukkan alamat email:")
            password = st.text_input("Masukkan password:", type="password")
            confirm_password = st.text_input("Konfirmasi password:", type="password")
            k1,k2 = st.columns([17.5,3])
            if k2.button("Buat Akun"):
                if password == confirm_password:
                    result = sign_up(email, password)
                    if result is None:
                        k1.success("Buat akun sukses. Ke Halaman Masuk Setelah Verifikasi Email")
                    else:
                        k1.error(f"Error: {result}")
                else:
                    k1.warning('Password tidak sama')

        elif selected_action == "Masuk":
            st.title('Masuk')
            email = st.text_input("Masukkan alamat email:")
            password = st.text_input("Masukkan password:", type="password")
            k1,k2 = st.columns([24,3])
            if k2.button("Masuk"):
                result = login(email, password)
                if result is None:
                    st.session_state.is_logged_in = True
                    st.experimental_rerun()
                else:
                    k1.error(f"Error: {result}")

        elif selected_action == "Reset Password":
            st.title('Reset Password')
            email = st.text_input("Masukkan alamat email:")
            k1,k2 = st.columns([20,5])
            if k2.button("Reset Password"):
                result = reset_password(email)
                if result is None:
                    k1.success("Password reset terkirim di email.")
                else:
                    k1.error(f"Error: {result}")

        elif selected_action == "Hapus Akun":
            st.title('Hapus Akun')
            email = st.text_input("Masukkan alamat email:")
            password = st.text_input("Masukkan password:", type="password")
            k1,k2 = st.columns([25.5,5])
            if k2.button("Hapus Akun"):
                result = delete_account(email, password)
                if result is None:
                    k1.success("Akun telah dihapus.")
                else:
                    k1.error(f"Error: {result}")

    else:
        def main():
            st.title("")

        with st.sidebar:
            selected_action = option_menu(
                menu_title="Main Menu",
                options=['Pemasukan','Pengeluaran','Perhitungan Keuangan'],
                icons=['cash-coin','cart-plus','calculator-fill'],
                menu_icon="list",
                default_index=0,
            )
            logout = st.button('Logout')
            if logout:
                st.session_state.is_logged_in = False
                st.experimental_rerun()
        
    if selected_action == "Pemasukan":
        def main():
            #walpapper
            img = get_img_as_base64("C:\\Users\\MAbdi\\OneDrive\\Dokumen\\Finish\\backgroundpemasukan.jpg")
            Walpaper_Pemasukan = f"""
                        <style>
                        [data-testid="stAppViewContainer"] > .main {{
                        background-image: url("data:image/png;base64,{img}");
                        background-size: cover;
                        background-position: top left;
                        background-repeat: repeat;
                        backgroung-attachment: fixed;
                        }}
                        </style>
                        """
            st.markdown(Walpaper_Pemasukan, unsafe_allow_html=True)
            st.title("Hitung Pemasukan")
            if 'income_data' not in st.session_state:
                st.session_state['income_data'] = []
            if 'total_income' not in st.session_state:
                st.session_state['total_income'] = 0
            if 'expense_data' not in st.session_state:
                st.session_state['expense_data'] = []

            #inputan
            new_source = st.text_input("Nama Pemasukan",help="Masukkan nama pemasukan")
            if new_source:
                st.session_state['income_sources'] = list(set(st.session_state.get('income_sources', []) + [new_source]))

            b1,b2,b3 = st.columns([8,4,3])
            income_source = b1.selectbox("Pilih Pemasukan", st.session_state.get('income_sources', []),help="Pilih nama pemasukan")
            income_amount = b2.number_input("Nominal (Rp)", step=10000, min_value=1000,help="Masukkan nominal pemasukan")
            date = b3.date_input("Tanggal",help="Pilih tanggal")

            #tombol
            col1, col2 = st.columns([15, 3])
            if col1.button("Tambah Pemasukan"):
                income_row = {"Nama Pemasukan": income_source, "Nominal": income_amount, "Tanggal": date}
                st.session_state['income_data'].append(income_row)
                st.session_state['total_income'] += income_amount

            if col2.button("Hapus Tabel", key="hapus_tabel_button"):
                if st.session_state['income_data']:
                    removed_row = st.session_state['income_data'].pop()
                    st.session_state['total_income'] -= removed_row.get('Nominal', 0)
            #ambil data
            df = pd.DataFrame(st.session_state['income_data'])
            df['Nomor'] = range(1, len(df) + 1)
            df.set_index('Nomor', inplace=True)
            if 'Nominal' in df.columns:
                df['Nominal'] = df['Nominal'].apply(lambda x: "Rp {:,.0f}".format(x).replace(',', '.'))
            #tabel
            st.dataframe(df.style.set_properties(**{'text-align': 'right'}), width=800)

            total_pemasukan = st.session_state.get('total_income', 0)
            total_pengeluaran = st.session_state.get('total_expense', 0)
            saldo_akhir = total_pemasukan - total_pengeluaran
            saldo_akhir = "{:,.0f}".format(saldo_akhir).replace(",", ".")
            total_pemasukan = "{:,.0f}".format(total_pemasukan).replace(",", ".")
            kol1,kol2 = st.columns([4.5,4.5])
            #tampilan
            if not df.empty:
                kol1.write(f"""
Total Pemasukan :

    Rp {total_pemasukan}
                """)
                kol2.write(f"""
Total Saldo :

    Rp {saldo_akhir}
                """)
            else:
                kol1.write("""
Total Pemasukan :

    Rp 0
                """)
                kol2.write("""
Total Saldo :

    Rp 0
                """)
                
            ko1,ko2 = st.columns([5.8,5])
            
            #download pemasukan
            if not df.empty:
                excel_path = "income_data.xlsx"
                df.to_excel(excel_path, index=False)
                with open(excel_path, 'rb') as f:
                    excel_data = f.read()
                b64 = base64.b64encode(excel_data).decode('utf-8')
                file_name = "data_pemasukan.xlsx"
                href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'

                # Style button
                button_style = """
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 15px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 5px;  /* Rounded corners */  
                """
                ko1.markdown(
                    f'<a href="{href}" download="{file_name}" style="{button_style}">Download Data Pemasukan</a>',
                    unsafe_allow_html=True
                )
            else:
                ko1.warning("Tidak ada data.")
            
            #download excel gabungan
            if not st.session_state['income_data'] and not st.session_state['expense_data']:
                ko2.warning("Tidak ada data.")
            else:
                df_income = pd.DataFrame(st.session_state['income_data'])
                df_expense = pd.DataFrame(st.session_state['expense_data'])

                if not df_income.empty and not df_expense.empty:
                    excel_path_combined = "data_gabungan(pemasukan & pengeluaran).xlsx"

                    with pd.ExcelWriter(excel_path_combined, engine='xlsxwriter') as writer:
                        bold_format = writer.book.add_format({'bold': True})
                        sheet_name = 'Data'
                        
                        if sheet_name not in writer.sheets:
                            writer.book.add_worksheet(sheet_name)
                        #label pemasukan    
                        writer.sheets[sheet_name].write(0, 0, "Pemasukan :", bold_format)
                        #tabel pemasukan
                        startrow_income = 1
                        df_income.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow_income, startcol=0)
                        #label pengeluaran
                        startrow_expense_label = startrow_income + len(df_income) + 3
                        writer.sheets[sheet_name].write(startrow_expense_label, 0, "Pengeluaran :", bold_format)
                        #tabel pengeluaran
                        startrow_expense = startrow_expense_label + 1
                        df_expense.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow_expense, startcol=0)
                        #label total
                        startrow_total_label = startrow_expense + len(df_expense) + 3
                        writer.sheets[sheet_name].write(startrow_total_label, 0, "Total :", bold_format)
                        #tabel total
                        total_pemasukan = df_income['Nominal'].sum()
                        total_pengeluaran = df_expense['Nominal'].sum()
                        saldo_akhir = total_pemasukan - total_pengeluaran
                        saldo_akhir_row = pd.DataFrame({'Total Pemasukan': [total_pemasukan], 'Total Pengeluaran': [total_pengeluaran], 'Saldo Akhir': [saldo_akhir]})
                        saldo_akhir_row.to_excel(writer, sheet_name=sheet_name, startrow=startrow_total_label + 1, startcol=0, index=False)

                        workbook = writer.book
                        worksheet_data = writer.sheets[sheet_name]

                        for _ in range(3):
                            worksheet_data.write_blank(worksheet_data.dim_colmax, 0, None)

                    with open(excel_path_combined, 'rb') as f:
                        excel_data_combined = f.read()

                    b64_combined = base64.b64encode(excel_data_combined).decode('utf-8')
                    file_name_combined = "data gabungan(pemasukan & pengeluaran)"
                    href_combined = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_combined}'

                    button_style_combined = """
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        cursor: pointer;
                        border-radius: 5px;
                    """

                    ko2.markdown(
                        f'<a href="{href_combined}" download="{file_name_combined}" style="{button_style_combined}">Download Data Pemasukan & Pengeluaran</a>',
                        unsafe_allow_html=True
                    )
                else:
                    ko2.warning("Tidak ada data Pengeluaran.")
                
            #grafik
            ba1,ba2,ba3 = st.columns([7,3,5])
            if not df.empty:
                ba1.subheader("Grafik Pemasukan")
                min_date = df['Tanggal'].min()
                max_date = df['Tanggal'].max()
                display_mode = ba2.selectbox("Pilih Mode Tampilan", ['Individu', 'Total'])
                date_range = ba3.date_input("Pilih Rentang Tanggal", [min_date, max_date], key='date_range')

                if isinstance(date_range, pd.Timestamp):
                    date_range = [date_range, date_range]

                filtered_df = df[(df['Tanggal'] >= date_range[0]) & (df['Tanggal'] <= date_range[1])]

                if not filtered_df.empty and 'Nominal' in filtered_df.columns:
                    filtered_df['Nominal'] = filtered_df['Nominal'].str.replace('Rp ', '').str.replace('.', '').astype(float)
                    filtered_df = filtered_df.sort_values(by=['Nomor'])
                    if display_mode == 'Total':
                        filtered_df = filtered_df.groupby('Nama Pemasukan')['Nominal'].sum().reset_index()

                        fig = px.line(
                            filtered_df,
                            x='Nama Pemasukan',
                            y='Nominal',
                            labels={'Nominal': 'Total Nominal'},
                            line_shape="linear",
                            template="plotly_dark",
                            hover_data={'Nominal': True},
                        )
                    else:
                        fig = px.line(
                            filtered_df,
                            x='Nama Pemasukan',
                            y='Nominal',
                            labels={'Nominal': 'Total Nominal'},
                            line_shape="linear",
                            template="plotly_dark",
                            hover_data={'Tanggal': True, 'Nominal': True},
                        )

                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )

                    fig.update_traces(
                        line=dict(color='#2E8A1F'),
                        marker=dict(size=8, color='green')
                    )

                    if display_mode == 'Total':
                        fig.update_traces(mode='lines+markers', hovertemplate='Nama Pemasukan : %{x}<br>Total Nominal : Rp %{y}')
                    else:
                        fig.update_traces(customdata=filtered_df[['Tanggal', 'Nominal', 'Nama Pemasukan']])
                        fig.update_traces(mode='lines+markers', hovertemplate='Nama Pemasukan : %{customdata[2]}<br>Tanggal : %{customdata[0]}<br>Total Nominal : Rp %{customdata[1]:,.0f}')

                    st.plotly_chart(fig)
                else:
                    st.warning("Tidak ada data untuk ditampilkan.")
            else:
                st.warning("Tidak ada data untuk ditampilkan.")


        if __name__ == "__main__":
            main()
    elif selected_action == "Pengeluaran":
        def main_pengeluaran():
            #wallpapper
            img = get_img_as_base64("C:\\Users\\MAbdi\\OneDrive\\Dokumen\\Finish\\backgroundpengeluaran.jpg")
            Walpaper_Pengeluaran = f"""
                                <style>
                                [data-testid="stAppViewContainer"] > .main {{
                                background-image: url("data:image/png;base64,{img}");
                                background-size: cover;
                                background-position: top left;
                                background-repeat: repeat;
                                backgroung-attachment: fixed;
                                }}
                                </style>
                                """
            st.markdown(Walpaper_Pengeluaran, unsafe_allow_html=True)
            st.title("Hitung Pengeluaran")
            if 'expense_data' not in st.session_state:
                st.session_state['expense_data'] = []
            if 'total_expense' not in st.session_state:
                st.session_state['total_expense'] = 0

            #input
            new_expense = st.text_input("Nama Pengeluaran", help="Masukkan nama pengeluaran")
            if new_expense:
                st.session_state['expense_list'] = list(set(st.session_state.get('expense_list', []) + [new_expense]))

            b1, b2, b3 = st.columns([8, 4, 3])
            expense_name = b1.selectbox("Pilih Pengeluaran", st.session_state.get('expense_list', []),
                                        help="Pilih nama pengeluaran")
            total_pemasukan = st.session_state.get('total_income', 0)
            total_pengeluaran = st.session_state.get('total_expense', 0)
            saldo_akhir = total_pemasukan - total_pengeluaran
            max_value = max(saldo_akhir, 0)
            default_value = max(min(max_value, 1000), 0)
            expense_amount = b2.number_input("Nominal (Rp)", step=10000, min_value=0, max_value=max_value,
                                            value=default_value,
                                            help="Masukkan pominal pengeluaran, Harus kurang atau sama dengan saldo akhir")

            date = b3.date_input("Tanggal", help="Pilih tanggal")
            # Tombol
            col1, col2 = st.columns([15, 3])
            if col1.button("Tambah Pengeluaran"):
                expense_row = {"Nama Pengeluaran": expense_name, "Nominal": expense_amount, "Tanggal": date}
                st.session_state['expense_data'].append(expense_row)
                st.session_state['total_expense'] += expense_amount

            if col2.button("Hapus Tabel", key="hapus_tabel_button"):
                if st.session_state['expense_data']:
                    removed_row = st.session_state['expense_data'].pop()
                    st.session_state['total_expense'] -= removed_row.get('Nominal', 0)

            # Ambil data
            df = pd.DataFrame(st.session_state['expense_data'])
            if not df.empty:
                total_pengeluaran = df['Nominal'].sum()
            else:
                total_pengeluaran = 0
            total_pemasukan = st.session_state.get('total_income', 0)
            total_pengeluaran = st.session_state.get('total_expense', 0)
            saldo_akhir = total_pemasukan - total_pengeluaran
            saldo_akhir = "{:,.0f}".format(saldo_akhir).replace(",", ".")
            total_pemasukan = "{:,.0f}".format(total_pemasukan).replace(",", ".")
            total_pengeluaran = "{:,.0f}".format(total_pengeluaran).replace(",", ".")
            df['Nomor'] = range(1, len(df) + 1)
            df.set_index('Nomor', inplace=True)
            if 'Nominal' in df.columns:
                df['Nominal'] = df['Nominal'].apply(lambda x: "Rp {:,.0f}".format(x).replace(',', '.'))
            df_style = df.style
            #tabel
            st.dataframe(df_style.set_properties(**{'text-align': 'right'}), width=800)
            kol1, kol2, kol3 = st.columns([3, 3, 3])
            #tampilan
            if not df.empty:
                kol2.write(f"""
        Total Pengeluaran :

            Rp {total_pengeluaran}
                """)
                kol1.write(f"""
        Saldo Dimiliki :

            Rp {total_pemasukan}
                """)
                kol3.write(f"""
        Saldo Akhir :

            Rp {saldo_akhir}
                """)
            else:
                kol2.write(f"""
        Total Pengeluaran :

            Rp 0
                """)
                kol1.write(f"""
        Saldo Dimiliki :

            Rp {total_pemasukan}
                """)
                kol3.write(f"""
        Saldo Akhir :

            Rp {saldo_akhir}
                """)

            ko1,ko2 = st.columns([5.8,5])
            #download
            if not df.empty:
                excel_path = "data_pengeluaran.xlsx"
                df.to_excel(excel_path, index=False)
                with open(excel_path, 'rb') as f:
                    excel_data = f.read()
                b64 = base64.b64encode(excel_data).decode('utf-8')
                file_name = "expense_data.xlsx"
                href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'

                button_style = """
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 15px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 5px;
                """

                ko1.markdown(
                    f'<a href="{href}" download="{file_name}" style="{button_style}">Download Data Pengeluaran</a>',
                    unsafe_allow_html=True
                )
            else:
                ko1.warning("Tidak ada data.")
            
            #download excel gabungan
            if not st.session_state['income_data'] and not st.session_state['expense_data']:
                ko2.warning("Tidak ada data.")
            else:
                df_income = pd.DataFrame(st.session_state['income_data'])
                df_expense = pd.DataFrame(st.session_state['expense_data'])

                if not df_income.empty and not df_expense.empty:
                    excel_path_combined = "data_gabungan(pemasukan & pengeluaran).xlsx"

                    with pd.ExcelWriter(excel_path_combined, engine='xlsxwriter') as writer:
                        bold_format = writer.book.add_format({'bold': True})
                        sheet_name = 'Data'
                        
                        if sheet_name not in writer.sheets:
                            writer.book.add_worksheet(sheet_name)
                        #label pemasukan    
                        writer.sheets[sheet_name].write(0, 0, "Pemasukan :", bold_format)
                        #tabel pemasukan
                        startrow_income = 1
                        df_income.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow_income, startcol=0)
                        #label pengeluaran
                        startrow_expense_label = startrow_income + len(df_income) + 3
                        writer.sheets[sheet_name].write(startrow_expense_label, 0, "Pengeluaran :", bold_format)
                        #tabel pengeluaran
                        startrow_expense = startrow_expense_label + 1
                        df_expense.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow_expense, startcol=0)
                        #label total
                        startrow_total_label = startrow_expense + len(df_expense) + 3
                        writer.sheets[sheet_name].write(startrow_total_label, 0, "Total :", bold_format)
                        #tabel total
                        total_pemasukan = df_income['Nominal'].sum()
                        total_pengeluaran = df_expense['Nominal'].sum()
                        saldo_akhir = total_pemasukan - total_pengeluaran
                        saldo_akhir_row = pd.DataFrame({'Total Pemasukan': [total_pemasukan], 'Total Pengeluaran': [total_pengeluaran], 'Saldo Akhir': [saldo_akhir]})
                        saldo_akhir_row.to_excel(writer, sheet_name=sheet_name, startrow=startrow_total_label + 1, startcol=0, index=False)

                        workbook = writer.book
                        worksheet_data = writer.sheets[sheet_name]

                        for _ in range(3):
                            worksheet_data.write_blank(worksheet_data.dim_colmax, 0, None)

                    with open(excel_path_combined, 'rb') as f:
                        excel_data_combined = f.read()

                    b64_combined = base64.b64encode(excel_data_combined).decode('utf-8')
                    file_name_combined = "data gabungan(pemasukan & pengeluaran)"
                    href_combined = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_combined}'

                    button_style_combined = """
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        cursor: pointer;
                        border-radius: 5px;
                    """

                    ko2.markdown(
                        f'<a href="{href_combined}" download="{file_name_combined}" style="{button_style_combined}">Download Data Pemasukan & Pengeluaran</a>',
                        unsafe_allow_html=True
                    )
                else:
                    ko2.warning("Tidak ada data Pengeluaran.")
                
            #grafik
            ba1,ba2,ba3 = st.columns([7,3,5])
            if not df.empty:
                ba1.subheader("Grafik Pengeluaran")
                min_date = df['Tanggal'].min()
                max_date = df['Tanggal'].max()
                display_mode = ba2.selectbox("Pilih Mode Tampilan", ['Individu', 'Total'])
                date_range = ba3.date_input("Pilih Rentang Tanggal", [min_date, max_date], key='date_range')

                if isinstance(date_range, pd.Timestamp):
                    date_range = [date_range, date_range]

                filtered_df = df[(df['Tanggal'] >= date_range[0]) & (df['Tanggal'] <= date_range[1])]

                if not filtered_df.empty and 'Nominal' in filtered_df.columns:
                    filtered_df['Nominal'] = filtered_df['Nominal'].str.replace('Rp ', '').str.replace('.', '').astype(float)
                    filtered_df = filtered_df.sort_values(by=['Nomor'])
                    if display_mode == 'Total':
                        filtered_df = filtered_df.groupby('Nama Pengeluaran')['Nominal'].sum().reset_index()

                        fig = px.line(
                            filtered_df,
                            x='Nama Pengeluaran',
                            y='Nominal',
                            labels={'Nominal': 'Total Nominal'},
                            line_shape="linear",
                            template="plotly_dark",
                            hover_data={'Nominal': True},
                        )
                    else:
                        fig = px.line(
                            filtered_df,
                            x='Nama Pengeluaran',
                            y='Nominal',
                            labels={'Nominal': 'Total Nominal'},
                            line_shape="linear",
                            template="plotly_dark",
                            hover_data={'Tanggal': True, 'Nominal': True},
                        )

                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )

                    fig.update_traces(
                        line=dict(color='#FF4B4B'),
                        marker=dict(size=8, color='red')
                    )

                    if display_mode == 'Total':
                        fig.update_traces(mode='lines+markers', hovertemplate='Nama Pengeluaran : %{x}<br>Total Nominal : Rp %{y}')
                    else:
                        fig.update_traces(customdata=filtered_df[['Tanggal', 'Nominal', 'Nama Pengeluaran']])
                        fig.update_traces(mode='lines+markers', hovertemplate='Nama Pengeluaran : %{customdata[2]}<br>Tanggal : %{customdata[0]}<br>Total Nominal : Rp %{customdata[1]:,.0f}')

                    st.plotly_chart(fig)
                else:
                    st.warning("Tidak ada data untuk ditampilkan.")
            else:
                st.warning("Tidak ada data untuk ditampilkan.")

        if __name__ == "__main__":
            main_pengeluaran()

    elif selected_action == 'Perhitungan Keuangan':
        def main():
            class FinancialCalculator:
                def __init__(self, background_image_path, excel_name, sheet_name):
                    self.background_image_path = background_image_path
                    self.excel_name = excel_name
                    self.sheet_name = sheet_name

                def display_background(self):
                    img = get_img_as_base64(self.background_image_path)
                    Walpaper = f"""
                                    <style>
                                    [data-testid="stAppViewContainer"] > .main {{
                                    background-image: url("data:image/png;base64,{img}");
                                    background-size: cover;
                                    background-position: top left;
                                    background-repeat: repeat;
                                    backgroung-attachment: fixed;
                                    }}
                                    </style>
                                    """
                    st.markdown(Walpaper, unsafe_allow_html=True)

                def save_data_to_excel(self, data):
                    data_df = pd.DataFrame(data)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    excel_path = os.path.join(script_dir, self.excel_name)

                    if not os.path.exists(excel_path):
                        data_df.to_excel(excel_path, index=False, sheet_name=self.sheet_name)
                    else:
                        existing_df = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')

                        if self.sheet_name in existing_df:
                            existing_df[self.sheet_name][['Biaya', 'Inflasi(%)']] = existing_df[self.sheet_name][['Biaya', 'Inflasi(%)']].astype(float)
                            combined_df = pd.concat([existing_df[self.sheet_name], data_df], ignore_index=True)
                            combined_df.to_excel(excel_path, index=False, sheet_name=self.sheet_name, engine='openpyxl')
                        else:
                            data_df.to_excel(excel_path, index=False, sheet_name=self.sheet_name, engine='openpyxl')

                    st.success(f"{self.sheet_name} berhasil ditambahkan ke file {self.excel_name}.")
                    download_file(excel_path, self.excel_name)
                    
                def save_data_to_excel_kpr(self, data):
                    data_df = pd.DataFrame(data)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    excel_path = os.path.join(script_dir, self.excel_name)

                    if not os.path.exists(excel_path):
                        data_df.to_excel(excel_path, index=False, sheet_name=self.sheet_name)
                    else:
                        existing_df = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')

                        if self.sheet_name in existing_df:
                            existing_df[self.sheet_name][['Pinjaman', 'Bunga(%)']] = existing_df[self.sheet_name][['Pinjaman', 'Bunga(%)']].astype(float)
                            combined_df = pd.concat([existing_df[self.sheet_name], data_df], ignore_index=True)
                            combined_df.to_excel(excel_path, index=False, sheet_name=self.sheet_name, engine='openpyxl')
                        else:
                            data_df.to_excel(excel_path, index=False, sheet_name=self.sheet_name, engine='openpyxl')

                    st.success(f"{self.sheet_name} berhasil ditambahkan ke file {self.excel_name}.")
                    download_file(excel_path, self.excel_name)
            selected = option_menu('Perhitungan Keuangan',
                           options=['Future Value', 'Dana KPR', 'Dana Pensiun'],
                           icons=['clock-history', 'calendar-check', 'credit-card'],
                           menu_icon="calculator",
                           default_index=0,
                           orientation="horizontal",
                           )

            if selected == 'Future Value':
                class FutureValueCalculator(FinancialCalculator):
                    def __init__(self):
                        super().__init__("C:\\Users\\MAbdi\\OneDrive\\Dokumen\\Finish\\backgroundfuturevalue.jpg", "Future Value.xlsx", "Future Value")

                    def calculate_future_value(self, initial_cost, inflation_rate1, target_year):
                        current_year = datetime.now().year
                        number_of_years = target_year - current_year
                        future_value = initial_cost * (1 + inflation_rate1) ** number_of_years

                        return future_value

                    def calculate_and_save(self, initial_cost, inflation_rate1, target_year):
                        future_value = self.calculate_future_value(initial_cost, inflation_rate1, target_year)

                        data = {
                            'Biaya': [float(initial_cost)],
                            'Inflasi(%)': [inflation_rate1],
                            'Target Tahun': [target_year],
                            'Hasil': [future_value]
                        }
                        future_value = "{:,.0f}".format(future_value).replace(",", ".")
                        st.write(f"""
                        Hasil: 
                        
                            Rp {future_value}""")

                        self.save_data_to_excel(data)
                calculator = FutureValueCalculator()

                # Display background image
                calculator.display_background()

                # Inputan
                initial_cost = st.number_input("Biaya Saat Ini:", step=10000, min_value=1000, help="Masukkan dana saat ini.")
                kolom1, kolom2 = st.columns([3, 7])
                inflation_rate1 = kolom1.number_input("Tingkat Inflasi (%):", step=1, min_value=1, help="Masukkan tingkat inflasi %.")
                current_year = datetime.now().year
                year_options = list(range(current_year + 1, current_year + 61))
                target_year = kolom2.selectbox(
                    "Tahun Dana Akan Digunakan:",
                    year_options,
                    index=0,
                    help="Pilih target tahun."
                )
                p1, p2 = st.columns([6.5, 3])
                hitung_button1 = p2.button('Hitung Biaya Di Masa Depan')
                if hitung_button1:
                    calculator.calculate_and_save(initial_cost, inflation_rate1, target_year)
                    

            elif selected == 'Dana KPR':
                class KPRCalculator(FinancialCalculator):
                    def __init__(self):
                        super().__init__("C:\\Users\\MAbdi\\OneDrive\\Dokumen\\Finish\\backgrounddanakpr.jpg", "Dana KPR.xlsx", "Dana KPR")

                    def calculate_monthly_installment(self, pinjaman, bunga, tenor_dalam_tahun, tenor_dalam_bulan):
                        cicilan_pokok = pinjaman / tenor_dalam_bulan
                        cicilan_bunga_per_bulan = pinjaman * bunga / 100 * tenor_dalam_tahun / tenor_dalam_bulan
                        total_cicilan_KPR_per_bulan = cicilan_pokok + cicilan_bunga_per_bulan

                        return total_cicilan_KPR_per_bulan

                    def calculate_and_save(self, pinjaman, bunga, tenor_dalam_tahun, tenor_dalam_bulan):
                        total_cicilan_KPR_per_bulan = self.calculate_monthly_installment(pinjaman, bunga, tenor_dalam_tahun, tenor_dalam_bulan)

                        data = {
                            'Pinjaman': [float(pinjaman)],
                            'Bunga(%)': [bunga],
                            'Tenor (tahun)': [tenor_dalam_tahun],
                            'Cicilan KPR per Bulan': [total_cicilan_KPR_per_bulan]
                        }
                        total_cicilan_KPR_per_bulan = "{:,.0f}".format(total_cicilan_KPR_per_bulan).replace(",", ".")
                        st.write(f"""
                        Cicilan Bulanan KPR Anda: 
                            
                            Rp {total_cicilan_KPR_per_bulan}""")

                        self.save_data_to_excel_kpr(data)
                calculator = KPRCalculator()

                # Display background image
                calculator.display_background()

                # Inputan
                pinjaman = st.number_input("Jumlah Pinjaman:", step=10000, min_value=1000, help="Masukkan nominal pinjaman.")
                p1, p2 = st.columns([2, 3])
                bunga = p1.number_input("Bunga Yang Diambil (%):", step=1, min_value=1, help="Masukkan persentase bunga.")
                tenor_dalam_tahun = p2.number_input("Tenor Yang Diambil (tahun):", step=1, min_value=1, help="Masukkan tenor per tahun.")
                tenor_dalam_bulan = tenor_dalam_tahun * 12

                k1, k2 = st.columns([10, 3])
                hitung_button2 = k2.button("Hitung Cicilan KPR")

                if hitung_button2:
                    calculator.calculate_and_save(pinjaman, bunga, tenor_dalam_tahun, tenor_dalam_bulan)

            elif selected == 'Dana Pensiun':
                class PensiunCalculator(FinancialCalculator):
                    def __init__(self):
                        super().__init__("C:\\Users\\MAbdi\\OneDrive\\Dokumen\\Finish\\backgrounddanapensiun.jpg", "Dana Pensiun.xlsx", "Dana Pensiun")

                    def calculate_retirement_savings(self, expense, inflation_rate2, retirement_age, current_age, life_expectation):
                        life_span = life_expectation - retirement_age
                        years_till_retirement = retirement_age - current_age
                        future_expenses = expense
                        future_expenses_inflation = future_expenses * (1 + inflation_rate2 / 100) ** years_till_retirement
                        retirement_savings_needed = future_expenses_inflation * 12 * life_span

                        return retirement_savings_needed

                    def calculate_and_save(self, expense, inflation_rate2, retirement_age, current_age, life_expectation):
                        retirement_savings_needed = self.calculate_retirement_savings(expense, inflation_rate2, retirement_age, current_age, life_expectation)

                        data = {
                            'Biaya': [float(expense)],
                            'Inflasi(%)': [inflation_rate2],
                            'Umur Pensiun': [retirement_age],
                            'Umur Sekarang': [current_age],
                            'Ekspetasi Hidup': [life_expectation],
                            'Dana Dibutuhkan': [retirement_savings_needed]
                        }
                        retirement_savings_needed = "{:,.0f}".format(retirement_savings_needed).replace(",", ".")
                        st.write(f"""
                        Dana pensiun yang dibutuhkan: 
                            
                            Rp {retirement_savings_needed}""")

                        self.save_data_to_excel(data)
                calculator = PensiunCalculator()

                calculator.display_background()

                c1, c2 = st.columns([9, 3])
                c3, c4, c5 = st.columns([5, 5, 5])

                # Inputan
                expense = c1.number_input("Jumlah Pengeluaran (Bulan) :", step=100000, min_value=100000, value=100000, help="Masukkan jumlah pengeluaran anda perbulan.")
                inflation_rate2 = c2.number_input("Tingkat Inflasi (%) :", step=1, min_value=1, help="Masukkan tingkat inflasi dalam persen.")
                current_age = c3.number_input("Umur Sekarang :", step=1, min_value=18, max_value=100, help="Masukkan umur Anda saat ini.")
                retirement_age = c4.number_input("Umur Pensiun :", step=1, min_value=current_age, max_value=100,  help="Masukkan usia saat anda ingin pensiun.")
                life_expectation = c5.number_input("Ekspetasi Hidup :", step=1, min_value=retirement_age, max_value=100, help="Masukkan usia ekspetasi hidup anda.")

                k1, k2 = st.columns([9, 3])
                hitung_button3 = k2.button("Hitung Dana Pensiun")

                if hitung_button3:
                    # Calculate and save data using PensiunCalculator
                    calculator.calculate_and_save(expense, inflation_rate2, retirement_age, current_age, life_expectation)

        if __name__ == '__main__':
            main()

app = GuiView()

