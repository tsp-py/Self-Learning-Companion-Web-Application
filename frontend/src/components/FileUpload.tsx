import React, { useCallback, useState } from 'react';
import {
  Box,
  Button,
  Text,
  VStack,
  useToast,
  Progress,
  Icon,
} from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';
import { AttachmentIcon } from '@chakra-ui/icons';

const FileUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const toast = useToast();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Check file size (max 25MB)
    if (file.size > 25 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Maximum file size is 25MB',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setUploading(true);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:5000/api/files/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      toast({
        title: 'Success',
        description: 'File uploaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to upload file',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }, [toast]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
    },
    multiple: false,
  });

  return (
    <VStack spacing={4} align="stretch">
      <Box
        {...getRootProps()}
        p={6}
        border="2px dashed"
        borderColor={isDragActive ? 'blue.400' : 'gray.200'}
        borderRadius="md"
        bg={isDragActive ? 'blue.50' : 'white'}
        cursor="pointer"
        transition="all 0.2s"
        _hover={{ borderColor: 'blue.400' }}
      >
        <input {...getInputProps()} />
        <VStack spacing={2}>
          <Icon as={AttachmentIcon} w={8} h={8} color="gray.400" />
          <Text textAlign="center" color="gray.500">
            {isDragActive
              ? 'Drop the file here'
              : 'Drag and drop a file here, or click to select'}
          </Text>
          <Text fontSize="sm" color="gray.400">
            Supported formats: PDF, DOCX, PPTX, TXT (max 25MB)
          </Text>
        </VStack>
      </Box>

      {uploading && (
        <Progress
          value={progress}
          size="sm"
          colorScheme="blue"
          isIndeterminate={progress === 0}
        />
      )}
    </VStack>
  );
};

export default FileUpload; 