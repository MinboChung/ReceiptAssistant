import os
import pandas as pd

class ExcelExporter():
    def __init__(self, path_folder:str, file_name:str, data:pd.DataFrame) -> None:
        print('ExcelExporter: allocated')
        self.path_folder = path_folder
        self.filename= file_name
        self.data = data
    
    def check_folder_and_export_excel(self):
        sheet_name = "Sheet1"

        if not os.path.exists(self.path_folder):
            os.makedirs(self.path_folder)
        file_path = os.path.join(self.path_folder, self.filename)
        if not os.path.exists(file_path):
            self.data.to_excel(file_path, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(file_path, mode='a', engine='openpyxl',if_sheet_exists='overlay') as writer:
                existing_sheets = writer.sheets
                if sheet_name not in existing_sheets:
                    self.data.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # self.data.to_excel(writer, sheet_name='Sheet1', index=False, startrow=existing_sheets['Sheet1'].max_row + 1) header=False removes column names when adding
                    self.data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=writer.sheets[sheet_name].max_row, header=False)
                writer._save()

