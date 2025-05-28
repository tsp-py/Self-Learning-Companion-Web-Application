import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  IconButton,
  useDisclosure,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  DrawerBody,
} from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';
import { useAuth } from '../contexts/AuthContext';
import FileUpload from '../components/FileUpload';
import LearningPaths from '../components/LearningPaths';
import Analytics from '../components/Analytics';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <Box minH="100vh">
      {/* Header */}
      <Flex
        as="header"
        align="center"
        justify="space-between"
        p={4}
        bg="white"
        boxShadow="sm"
      >
        <HStack spacing={4}>
          <IconButton
            aria-label="Open menu"
            icon={<HamburgerIcon />}
            onClick={onOpen}
            display={{ base: 'flex', md: 'none' }}
          />
          <Heading size="md">SoloLearn</Heading>
        </HStack>

        <HStack spacing={4}>
          <Text>Welcome, {user?.name}</Text>
          <Button colorScheme="blue" variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </HStack>
      </Flex>

      {/* Main Content */}
      <Flex>
        {/* Sidebar */}
        <Box
          w={{ base: '0', md: '250px' }}
          h="calc(100vh - 64px)"
          bg="white"
          boxShadow="sm"
          p={4}
          display={{ base: 'none', md: 'block' }}
        >
          <VStack align="stretch" spacing={4}>
            <Button variant="ghost" justifyContent="flex-start">
              Dashboard
            </Button>
            <Button variant="ghost" justifyContent="flex-start">
              Learning Paths
            </Button>
            <Button variant="ghost" justifyContent="flex-start">
              Analytics
            </Button>
          </VStack>
        </Box>

        {/* Content Area */}
        <Box flex={1} p={4}>
          <VStack spacing={8} align="stretch">
            <FileUpload />
            <LearningPaths />
            <Analytics />
          </VStack>
        </Box>
      </Flex>

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>SoloLearn</DrawerHeader>
          <DrawerBody>
            <VStack align="stretch" spacing={4}>
              <Button variant="ghost" justifyContent="flex-start">
                Dashboard
              </Button>
              <Button variant="ghost" justifyContent="flex-start">
                Learning Paths
              </Button>
              <Button variant="ghost" justifyContent="flex-start">
                Analytics
              </Button>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default Dashboard; 