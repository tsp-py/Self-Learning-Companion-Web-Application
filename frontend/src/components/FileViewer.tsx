import React, { useState, useEffect } from 'react';
import {
  Box,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  Button,
  useToast,
  Spinner,
} from '@chakra-ui/react';
import { Document, Page } from 'react-pdf';
import mammoth from 'mammoth';
import { tracking } from '../api/client';
import type { File } from '../types';

interface FileViewerProps {
  file: File;
  isOpen: boolean;
  onClose: () => void;
}

const FileViewer: React.FC<FileViewerProps> = ({ file, isOpen, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState<string>('');
  const [numPages, setNumPages] = useState<number | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const toast = useToast();

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const startSession = async () => {
      try {
        const session = await tracking.startSession(file.id);
        setSessionId(session.id);
      } catch (error) {
        console.error('Failed to start session:', error);
      }
    };

    const endSession = async () => {
      if (sessionId) {
        try {
          await tracking.endSession(sessionId);
        } catch (error) {
          console.error('Failed to end session:', error);
        }
      }
    };

    if (isOpen) {
      startSession();
      interval = setInterval(() => {
        // Simulate activity by updating the session
        if (sessionId) {
          tracking.endSession(sessionId).then((session) => {
            setSessionId(session.id);
          });
        }
      }, 30000); // Every 30 seconds
    }

    return () => {
      clearInterval(interval);
      endSession();
    };
  }, [isOpen, file.id, sessionId]);

  useEffect(() => {
    const loadContent = async () => {
      setLoading(true);
      try {
        if (file.type === 'pdf') {
          // PDF is handled by react-pdf
          setLoading(false);
        } else if (file.type === 'docx') {
          const response = await fetch(file.path);
          const arrayBuffer = await response.arrayBuffer();
          const result = await mammoth.extractRawText({ arrayBuffer });
          setContent(result.value);
          setLoading(false);
        } else if (file.type === 'txt') {
          const response = await fetch(file.path);
          const text = await response.text();
          setContent(text);
          setLoading(false);
        }
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to load file content',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        setLoading(false);
      }
    };

    if (isOpen) {
      loadContent();
    }
  }, [isOpen, file, toast]);

  const handleDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="full">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{file.name}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {loading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minH="50vh">
              <Spinner size="xl" />
            </Box>
          ) : file.type === 'pdf' ? (
            <Box>
              <Document
                file={file.path}
                onLoadSuccess={handleDocumentLoadSuccess}
              >
                <Page pageNumber={currentPage} />
              </Document>
              {numPages && (
                <Box mt={4} textAlign="center">
                  <Button
                    mr={2}
                    onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                    disabled={currentPage <= 1}
                  >
                    Previous
                  </Button>
                  <span>
                    Page {currentPage} of {numPages}
                  </span>
                  <Button
                    ml={2}
                    onClick={() =>
                      setCurrentPage((prev) => Math.min(prev + 1, numPages))
                    }
                    disabled={currentPage >= numPages}
                  >
                    Next
                  </Button>
                </Box>
              )}
            </Box>
          ) : (
            <Box
              whiteSpace="pre-wrap"
              fontFamily="monospace"
              p={4}
              bg="gray.50"
              borderRadius="md"
            >
              {content}
            </Box>
          )}
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={onClose}>
            Close
          </Button>
          <Button variant="ghost" onClick={() => {
            if (sessionId) {
              tracking.endSession(sessionId);
            }
            onClose();
          }}>
            Mark as Complete
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default FileViewer; 