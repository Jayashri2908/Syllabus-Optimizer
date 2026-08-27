import React, { useRef, useState, DragEvent, ChangeEvent } from 'react';
import { UploadCloud } from 'lucide-react';
import { FileUploaderProps } from '../types';
import SkeletonLoader from './SkeletonLoader';
import toast from 'react-hot-toast';
import './FileUploader.css';

const VALID_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
const VALID_EXTENSIONS = ['.pdf', '.docx', '.txt'];
const MAX_SIZE_MB = 50;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

const FileUploader: React.FC<FileUploaderProps> = ({ onUpload, isLoading }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!VALID_TYPES.includes(file.type) && !VALID_EXTENSIONS.includes(ext)) {
      toast.error('Invalid file type. Please upload a PDF, DOCX, or TXT file.');
      return false;
    }
    if (file.size > MAX_SIZE_BYTES) {
      toast.error(`File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum: ${MAX_SIZE_MB} MB.`);
      return false;
    }
    return true;
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) onUpload(file);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>): void => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) onUpload(file);
    }
  };

  return (
    <div 
      className={`file-uploader ${isDragActive ? 'active' : ''} ${isLoading ? 'loading' : ''}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={() => !isLoading && fileInputRef.current?.click()}
      role="button"
      tabIndex={0}
      aria-label="Upload syllabus file. Supports PDF, DOCX, and TXT formats."
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInputRef.current?.click(); } }}
    >
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleChange} 
        style={{ display: 'none' }} 
        accept=".pdf,.docx,.txt"
      />
      
      {isLoading ? (
        <div style={{ width: '100%', maxWidth: '600px', margin: '0 auto', textAlign: 'left' }}>
          <h3 className="mb-4">Extracting Document Architecture...</h3>
          <SkeletonLoader count={4} />
          <br/>
          <SkeletonLoader type="chart" />
        </div>
      ) : (
        <div className="uploader-content">
          <UploadCloud className="upload-icon" size={48} />
          <h3>Drag & Drop Syllabus File</h3>
          <p>Or click to browse (PDF, DOCX, TXT — max {MAX_SIZE_MB} MB)</p>
          <div className="upload-btn">Select File</div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
