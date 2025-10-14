# TODO: Fix AttributeError in AttendanceExportView

## Steps to Complete

- [ ] Update ExportMixin.get_filename method to accept request as first parameter
- [ ] Update TrainingExportView.export_csv to pass self.request to get_filename
- [ ] Update TrainingExportView.export_excel to pass self.request to get_filename
- [ ] Update AttendanceExportView.export_csv to pass self.request to get_filename
- [ ] Update AttendanceExportView.export_excel to pass self.request to get_filename
- [ ] Update PayrollExportView.export_csv to pass self.request to get_filename
- [ ] Update PayrollExportView.export_excel to pass self.request to get_filename
- [ ] Update EmployeeExportView.export_csv to pass self.request to get_filename
- [ ] Update EmployeeExportView.export_excel to pass self.request to get_filename
- [ ] Update LeaveApplicationExportView.export_csv to pass self.request to get_filename
- [ ] Update LeaveApplicationExportView.export_excel to pass self.request to get_filename
- [ ] Test the export functionality to ensure the error is resolved
