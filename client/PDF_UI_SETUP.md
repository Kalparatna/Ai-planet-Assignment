# PDF UI Setup Guide

This guide explains the UI changes made to support PDF upload and querying functionality in your Math Routing Agent.

## 🎯 **New Features Added**

### **1. PDF Upload & Management**
- Drag & drop PDF upload interface
- File validation (PDF only, 10MB max)
- Upload progress and status feedback
- PDF management with list, select, and delete functionality

### **2. Enhanced Math Routing**
- PDF content is now checked in the routing pipeline
- Visual indicators show when PDF content is used
- Context-aware query form shows selected PDF

### **3. Tabbed Interface**
- **Math Query Tab**: Original functionality with PDF context
- **PDF Documents Tab**: Upload and manage PDFs
- **History Tab**: Query history management

## 🚀 **Installation Steps**

### **1. Install Dependencies**
```bash
cd client
npm install
```

This will install the new `lucide-react` dependency for icons.

### **2. Start the Development Server**
```bash
npm run dev
```

### **3. Start the Backend Server**
```bash
cd ../server
python main.py
```

## 📋 **New UI Components**

### **1. PDFUpload.jsx**
- Drag & drop file upload
- File validation and size checking
- Upload progress indication
- Success/error status messages

### **2. PDFManager.jsx**
- List all uploaded PDFs
- Select PDF for priority querying
- Delete PDFs with confirmation
- Show PDF metadata (pages, chunks, upload time)

### **3. PDFTab.jsx**
- Tabbed interface for PDF operations
- Upload and Manage sub-tabs
- Integration with main app state

### **4. Updated Components**
- **App.jsx**: Added tabbed interface and PDF state management
- **QueryForm.jsx**: Shows PDF context when selected
- **SolutionDisplay.jsx**: Enhanced source indicators and PDF-specific styling

## 🎨 **UI Features**

### **PDF Upload Interface**
- Clean drag & drop area
- Visual feedback during upload
- File type and size validation
- Success confirmation with file details

### **PDF Management**
- Grid view of uploaded PDFs
- Click to select/deselect PDFs
- Visual indicators for selected PDF
- Delete functionality with confirmation

### **Enhanced Query Interface**
- PDF context indicator when PDF is selected
- Source-specific styling in solutions
- Clear visual hierarchy with tabs

### **Solution Display Improvements**
- Color-coded source indicators:
  - 🟣 Purple: PDF Document
  - 🔵 Blue: Web Search  
  - 🟢 Green: Knowledge Base
  - 🟠 Orange: AI Generated
- Better formatting for mathematical content
- Reference links and PDF source indicators

## 🔄 **User Workflow**

### **1. Upload PDF**
1. Go to "PDF Documents" tab
2. Click "Upload PDF" sub-tab
3. Drag & drop or click to select PDF file
4. Wait for processing completion
5. Switch to "Manage PDFs" to see uploaded file

### **2. Select PDF for Queries**
1. In "Manage PDFs" sub-tab
2. Click on a PDF to select it
3. Selected PDF shows with checkmark
4. Go to "Math Query" tab to ask questions

### **3. Ask Questions**
1. In "Math Query" tab
2. Type your question (PDF context shown if selected)
3. System will search PDF first, then other sources
4. Solution shows source type with color coding

### **4. Manage PDFs**
1. View all uploaded PDFs in "Manage PDFs"
2. See metadata: pages, chunks, upload time
3. Delete PDFs using trash icon
4. Select/deselect PDFs for priority querying

## 🎯 **Integration with Backend**

### **API Endpoints Used**
- `POST /pdf/upload` - Upload PDF files
- `GET /pdf/list` - List uploaded PDFs
- `POST /pdf/query` - Query PDF content directly
- `DELETE /pdf/{file_id}` - Delete uploaded PDFs
- `POST /math/solve` - Enhanced to include PDF content

### **Enhanced Math Routing**
The routing pipeline now follows:
```
User Query → Knowledge Base → PDF Content → Web Search → AI Generation
```

### **Source Indicators**
- Solutions show which source provided the answer
- PDF sources include filename in references
- Confidence scores reflect source reliability

## 🎨 **Styling & UX**

### **Design Principles**
- Consistent with existing Tailwind CSS styling
- Clear visual hierarchy with tabs
- Intuitive drag & drop interface
- Responsive design for different screen sizes

### **Color Scheme**
- Blue: Primary actions and selected states
- Purple: PDF-related features
- Green: Success states and knowledge base
- Red: Error states and warnings
- Gray: Secondary information

### **Icons**
Using Lucide React icons for consistency:
- Upload, FileText, Search, Calculator, History
- Trash2, Eye, Calendar, Hash, MessageSquare
- CheckCircle, AlertCircle, X

## 🔧 **Customization**

### **File Size Limits**
Change in `PDFUpload.jsx`:
```javascript
if (file.size > 10 * 1024 * 1024) { // Change 10MB limit
```

### **Supported File Types**
Currently PDF only, but can be extended in:
```javascript
accept=".pdf" // Add other types like .doc,.txt
```

### **Styling**
All components use Tailwind CSS classes and can be customized by modifying the className attributes.

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Upload fails**: Check file size (max 10MB) and type (PDF only)
2. **PDF not showing**: Refresh the PDF list or check server logs
3. **Icons not showing**: Ensure `lucide-react` is installed
4. **Styling issues**: Check Tailwind CSS is properly configured

### **Debug Steps**
1. Check browser console for JavaScript errors
2. Check network tab for API call failures
3. Verify backend server is running on port 8000
4. Check server logs for PDF processing errors

## 📱 **Mobile Responsiveness**

The interface is designed to work on mobile devices:
- Responsive tabs that stack on small screens
- Touch-friendly drag & drop areas
- Appropriate text sizes and spacing
- Mobile-optimized file upload interface

## 🎉 **Success Indicators**

You'll know everything is working when:
- ✅ You can drag & drop PDF files successfully
- ✅ Uploaded PDFs appear in the management interface
- ✅ Selecting a PDF shows context in the query form
- ✅ Math queries return answers from PDF content
- ✅ Solution display shows "PDF Document" as source
- ✅ All tabs navigate smoothly without errors

Your Math Routing Agent now has full PDF support with a professional, user-friendly interface! 🚀