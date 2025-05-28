import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  Heading,
  HStack,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorModeValue,
} from '@chakra-ui/react';
import { Line, Pie } from 'react-chartjs-2';
import { tracking } from '../api/client';
import type { Stats } from '../types';

const Analytics: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const cardBg = useColorModeValue('white', 'gray.700');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await tracking.getStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, []);

  if (!stats) return null;

  const totalHours = Math.round(stats.total_time / 3600);
  const completedFiles = stats.by_file.filter((f) => f.seconds > 0).length;

  const timeByTypeData = {
    labels: stats.by_type.map((t) => t.type.toUpperCase()),
    datasets: [
      {
        data: stats.by_type.map((t) => Math.round(t.seconds / 3600)),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
        ],
      },
    ],
  };

  const dailyActivityData = {
    labels: stats.daily_activity.map((d) =>
      new Date(d.date).toLocaleDateString()
    ),
    datasets: [
      {
        label: 'Hours',
        data: stats.daily_activity.map((d) =>
          Math.round(d.seconds / 3600)
        ),
        fill: false,
        borderColor: '#36A2EB',
        tension: 0.1,
      },
    ],
  };

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        <Heading size="md">Analytics</Heading>

        <HStack spacing={4}>
          <Stat
            p={4}
            bg={cardBg}
            borderRadius="lg"
            boxShadow="sm"
          >
            <StatLabel>Total Learning Time</StatLabel>
            <StatNumber>{totalHours}h</StatNumber>
            <StatHelpText>All time</StatHelpText>
          </Stat>

          <Stat
            p={4}
            bg={cardBg}
            borderRadius="lg"
            boxShadow="sm"
          >
            <StatLabel>Files Completed</StatLabel>
            <StatNumber>{completedFiles}</StatNumber>
            <StatHelpText>Total files</StatHelpText>
          </Stat>
        </HStack>

        <HStack spacing={4} align="stretch">
          <Box
            flex={1}
            p={4}
            bg={cardBg}
            borderRadius="lg"
            boxShadow="sm"
          >
            <Heading size="sm" mb={4}>
              Time by File Type
            </Heading>
            <Pie data={timeByTypeData} />
          </Box>

          <Box
            flex={2}
            p={4}
            bg={cardBg}
            borderRadius="lg"
            boxShadow="sm"
          >
            <Heading size="sm" mb={4}>
              Daily Activity
            </Heading>
            <Line
              data={dailyActivityData}
              options={{
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Hours',
                    },
                  },
                },
              }}
            />
          </Box>
        </HStack>
      </VStack>
    </Box>
  );
};

export default Analytics; 