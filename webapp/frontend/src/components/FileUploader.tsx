import React, { useRef, useState, DragEvent, ChangeEvent } from 'react';
import { UploadCloud } from 'lucide-react';
import { FileUploaderProps } from '../types';
import SkeletonLoader from './SkeletonLoader';
import './FileUploader.css';

const FileUploader: React.FC<FileUploaderProps> = ({ onUpload, isLoading }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>): void => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
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
          <p>Or click to browse (PDF, DOCX, TXT)</p>
          <div className="upload-btn">Select File</div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
