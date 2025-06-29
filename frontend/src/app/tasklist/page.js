'use client';
import React, {useEffect} from 'react';
import { Button, Form, Input, Card, DatePicker, Table, Tag, Space, InputNumber, Tooltip, message, AutoComplete, Select, TimePicker } from 'antd';
import { useRouter } from 'next/navigation';
import { 
    LinkOutlined, 
    CalendarOutlined, 
    SearchOutlined, 
    ClockCircleOutlined, 
    VideoCameraOutlined,
    EyeOutlined,
    DeleteOutlined,
    FileSearchOutlined,
    EditOutlined,
    FileTextOutlined
} from '@ant-design/icons';

export default function TaskListPage() {
    const router = useRouter();
    const [loading, setLoading] = React.useState(false);
    
    // Sample data for the task list table
    const [tasks, setTasks] = React.useState([]);

    const categoryOptions = [
        { label: 'Bangladesh', value: 'bangladesh' },
        { label: 'World', value: 'world' }, 
        { label: 'Opinion', value: 'opinion' },
        { label: 'Business', value: 'business' },
        { label: 'Entertainment', value: 'entertainment' },
        { label: 'Lifestyle', value: 'lifestyle' },
        { label: 'Chakri', value: 'chakri' },
        { label: 'Sports', value: 'sports' },
        { label: 'Technology', value: 'technology' },
        { label: 'Education', value: 'education' },
        { label: 'Religion', value: 'religion' },
        { label: 'Onnoalo', value: 'onnoalo' },
        { label: 'Roundtable', value: 'roundtable' },
        { label: 'Special Supplement', value: 'special-supplement' },
        { label: 'Anniversary', value: 'anniversary' },
        { label: 'Fun', value: 'fun' }
    ];


    useEffect(() => {

        const fetchTasks = async() => {
            setLoading(true)
            try {
                const response = await fetch("http://127.0.0.1:8000/api/tasks/");

                if (!response.ok)
                    throw new Error(`HTTP error! status : ${response.status}`)

                const data = await response.json();

                const transformedData = data.map(task => ({
                    ...task,
                    current_contents:  0,
                    key: task.id  // Add key for React
                }));

                setTasks(transformedData);

            }

            catch(error) {
                console.error("Error fetching tasks:", error);
                message.error("Failed to fetch tasks. Please try again later.");
            }
            finally {
                setLoading(false);
            }
        }

        fetchTasks();

    }, []);

    const formatNumber = (num) => {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num;
    };
    
    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };


    const goToTaskViewContent = async (taskId) => {
        router.push(`/tasklist/view-content/${taskId}`);
    }

    const goToTaskEditContent = async (taskId) => {
        router.push(`/tasklist/edit-content/${taskId}`);
    }

    const goToGenericSearch = async () => {
        router.push('/generic-search');
    }


    const goToTaskDeleteContent = async (taskId) => {
        setLoading(true);

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/tasks/${taskId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status : ${response.status}`);
            }

            setTasks(prev => prev.filter(task => task.id !== taskId));
            message.success("Task deleted successfully!");

        }
        catch(error) {
            console.error("Error deleting task:", error);
            message.error("Failed to delete task. Please try again later.");
        }
        finally {
            setLoading(false);
        }
    }

    const convertMinutesToHoursMinutes = (totalMinutes) => {
        if (!totalMinutes) return '-';
        
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        
        if (hours === 0) {
            return `${minutes}m`;
        } else if (minutes === 0) {
            return `${hours}h`;
        } else {
            return `${hours}h ${minutes}m`;
        }
    };

    const columns = [
        {
            title: 'Category',
            dataIndex: 'category',
            key: 'category',
            render: (text, record) => <a href={record.url} target="_blank" rel="noopener noreferrer">{text.charAt(0).toUpperCase() + text.slice(1)}</a>,
        },

        {
            title: 'Scheduled Hours',
            dataIndex: 'scheduled_hours',
            key: 'scheduled_hours',
            width: 100,
            render: (minutes) => convertMinutesToHoursMinutes(minutes),
        },
        {
            title: 'Contents',
            children: [
                {
                    title: 'Current',
                    dataIndex: 'content_count',
                    key: 'current_contents',
                    width: 100,
                    align: 'center',
                },
                {
                    title: 'Max',
                    dataIndex: 'max_contents',
                    key: 'max_contents',
                    width: 80,
                    align: 'center',
                }
            ]
        },

        {
            title: 'End Time',
            dataIndex: 'end_time',
            key: 'end_time',
            width: 180,
            render: (date) => {
                return formatDate(date);
            },
        },

        {
            title: 'Status',
            key: 'is_active',
            dataIndex: 'is_active',
            width: 100,
            render: (active) => {
                return (
                    <Tag color={active ? 'green' : 'volcano'}>
                        {active ? 'ACTIVE' : 'INACTIVE'}
                    </Tag>
                );
            },
        },
        {
            title: 'Created At',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date) => formatDate(date),
        },
        {
            title: 'Last Scraped',
            dataIndex: 'last_scraped_at',
            key: 'last_scraped_at',
            render: (date) => formatDate(date),
        },
        {
            title: 'Action',
            key: 'action',
            width: 120,
            render: (_, record) => (
                <Space size="middle">
                    <Tooltip title="View Contents">
                        <Button type="link" icon={<EyeOutlined />} onClick={() => goToTaskViewContent(record.id)} />
                    </Tooltip>
                    <Tooltip title="Edit">
                        <Button type="link" icon={<EditOutlined />} onClick={() => goToTaskEditContent(record.id)} />
                    </Tooltip>
                    <Tooltip title="Delete">
                        <Button type="link" danger icon={<DeleteOutlined />} onClick={() => goToTaskDeleteContent(record.id)} />
                    </Tooltip>
                </Space>
            ),
        },
    ];
    
    const onFinish = async(values) => {
        setLoading(true);

        try {

            let scheduledMinutes = null;

            if (values.scheduled_hours) {
                const hours = values.scheduled_hours.hour();
                const minutes = values.scheduled_hours.minute();
                scheduledMinutes = hours * 60 + minutes;
            }

            const payload = {
                ...values,
                category: values.category.toLowerCase(),
                scheduled_hours: scheduledMinutes,
                end_time: values.endTime ? values.endTime.format('YYYY-MM-DD HH:mm:ss') : null
            }



            const response = await fetch("http://127.0.1:8000/api/tasks/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status : ${response.status}`);
            }

            const task = await response.json();
            message.success("Task assigned successfully!");

            setTasks(prev => [
                {...task, current_contents:0, key: task.id},
                ...prev
            ])

        }
        catch(error) {
            console.error("Error assigning task:", error);
            message.error("Failed to assign task. Please try again later.");
        }
        finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "30px" }}>
            <h1 style={{ fontSize: '28px', marginBottom: '20px', color: '#1890ff' }}>
                Prothom Alo Scraping System
            </h1>
                
            <Card 
                title="Assign Monitoring Task" 
                style={{ 
                    width: '100%',
                    boxShadow: '0px 5px 15px rgba(180, 255, 150, 0.4)',
                    borderRadius: '8px'
                }}
            >
                <Form
                    name="taskAssignment"
                    layout="inline"
                    onFinish={onFinish}
                >
                    <Form.Item
                        name="category"
                        rules={[{ required: true, message: 'News Category required!' }]}
                        style={{ minWidth: '250px', flex: 2 }}
                    >
                        
                        <Select
                            options={categoryOptions}
                            style={{ width: '100%' }}
                            placeholder="Select News Category"
                            allowClear
                            showSearch
                            filterOption={(input, option) =>
                                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                            }
                        />


                    </Form.Item>
                    
                    <Form.Item
                        name="endTime"
                        style={{ minWidth: '350px', flex: 1 }}
                    >
                        <DatePicker 
                            showTime 
                            format="YYYY-MM-DD HH:mm:ss"
                            placeholder="End Time (Default: 1 hour later)"
                            style={{ width: '100%' }}
                        />
                    </Form.Item>
                    
                    <Form.Item
                        name="scheduled_hours"
                        style={{ minWidth: '200px', flex: 0.5 }}
                    >
                        <TimePicker
                            format="HH:mm"
                            placeholder="Hours:Minutes"
                            style={{ width: '100%' }}
                            showNow={false}
                            minuteStep={5}
                            suffixIcon={<ClockCircleOutlined />}
                        />
                    </Form.Item>
                    
                    <Form.Item
                        name="max_contents"
                        style={{ minWidth: '200px', flex: 0.5 }}
                    >
                        <InputNumber
                            min={1}
                            max={100}
                            prefix={<FileTextOutlined />}
                            placeholder="Max Contents"
                            style={{ width: '100%' }}
                        />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading} icon={<SearchOutlined />}>
                            Assign Task
                        </Button>
                    </Form.Item>
                </Form>
            </Card>

            <Card
                title="Category Scraping Tasks"
                style={{ 
                    width: '100%',
                    boxShadow: '0px 5px 15px rgba(0, 0, 0, 0.1)',
                    borderRadius: '8px'
                }}
                loading={loading}
                extra={
                    <Button icon={<FileSearchOutlined />} onClick={goToGenericSearch}>
                        Search & Filter
                    </Button>
                }

                


            >
                <Table 
                    columns={columns} 
                    dataSource={tasks}
                    pagination={{ pageSize: 10 }}
                    bordered
                    scroll={{ x: 'max-content' }}
                    size="middle"
                />
            </Card>
        </div>
    );
}