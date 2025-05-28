import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  Heading,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  useToast,
} from '@chakra-ui/react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { paths, files } from '../api/client';
import type { LearningPath, File } from '../types';

const LearningPaths: React.FC = () => {
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [availableFiles, setAvailableFiles] = useState<File[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<number[]>([]);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [newPath, setNewPath] = useState({
    title: '',
    description: '',
  });
  const toast = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [pathsData, filesData] = await Promise.all([
          paths.list(),
          files.list(),
        ]);
        setLearningPaths(pathsData);
        setAvailableFiles(filesData);
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to fetch data',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      }
    };

    fetchData();
  }, [toast]);

  const handleCreatePath = async () => {
    try {
      if (!newPath.title || selectedFiles.length === 0) {
        toast({
          title: 'Error',
          description: 'Title and at least one file are required',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      const path = await paths.create({
        ...newPath,
        resources: selectedFiles,
      });

      setLearningPaths([...learningPaths, path]);
      setNewPath({ title: '', description: '' });
      setSelectedFiles([]);
      onClose();

      toast({
        title: 'Success',
        description: 'Learning path created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create learning path',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const items = Array.from(selectedFiles);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setSelectedFiles(items);
  };

  return (
    <Box>
      <VStack spacing={4} align="stretch">
        <HStack justify="space-between">
          <Heading size="md">Learning Paths</Heading>
          <Button colorScheme="blue" onClick={onOpen}>
            Create New Path
          </Button>
        </HStack>

        {learningPaths.map((path) => (
          <Box
            key={path.id}
            p={4}
            borderWidth={1}
            borderRadius={8}
            bg="white"
            boxShadow="sm"
          >
            <VStack align="stretch" spacing={4}>
              <Heading size="sm">{path.title}</Heading>
              <Text>{path.description}</Text>
              <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="resources">
                  {(provided) => (
                    <VStack
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      spacing={2}
                    >
                      {path.resources.map((resource, index) => (
                        <Draggable
                          key={resource.id}
                          draggableId={resource.id.toString()}
                          index={index}
                        >
                          {(provided) => (
                            <Box
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              p={2}
                              bg="gray.50"
                              borderRadius={4}
                              w="full"
                            >
                              <Text>{resource.file_name}</Text>
                            </Box>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </VStack>
                  )}
                </Droppable>
              </DragDropContext>
            </VStack>
          </Box>
        ))}
      </VStack>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create New Learning Path</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Title</FormLabel>
                <Input
                  value={newPath.title}
                  onChange={(e) =>
                    setNewPath({ ...newPath, title: e.target.value })
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={newPath.description}
                  onChange={(e) =>
                    setNewPath({ ...newPath, description: e.target.value })
                  }
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Resources</FormLabel>
                <Select
                  placeholder="Select files"
                  onChange={(e) => {
                    const fileId = parseInt(e.target.value);
                    if (!selectedFiles.includes(fileId)) {
                      setSelectedFiles([...selectedFiles, fileId]);
                    }
                  }}
                >
                  {availableFiles.map((file) => (
                    <option key={file.id} value={file.id}>
                      {file.name}
                    </option>
                  ))}
                </Select>
              </FormControl>

              <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="selected-files">
                  {(provided) => (
                    <VStack
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      spacing={2}
                      w="full"
                    >
                      {selectedFiles.map((fileId, index) => {
                        const file = availableFiles.find((f) => f.id === fileId);
                        return (
                          <Draggable
                            key={fileId}
                            draggableId={fileId.toString()}
                            index={index}
                          >
                            {(provided) => (
                              <Box
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                {...provided.dragHandleProps}
                                p={2}
                                bg="gray.50"
                                borderRadius={4}
                                w="full"
                              >
                                <HStack justify="space-between">
                                  <Text>{file?.name}</Text>
                                  <IconButton
                                    aria-label="Remove file"
                                    icon={<FiX />}
                                    size="sm"
                                    onClick={() =>
                                      setSelectedFiles(
                                        selectedFiles.filter((id) => id !== fileId)
                                      )
                                    }
                                  />
                                </HStack>
                              </Box>
                            )}
                          </Draggable>
                        );
                      })}
                      {provided.placeholder}
                    </VStack>
                  )}
                </Droppable>
              </DragDropContext>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handleCreatePath}>
              Create
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default LearningPaths; 