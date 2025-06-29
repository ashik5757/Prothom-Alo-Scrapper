'use client';

import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Spin, Typography, Divider, Descriptions, message, Form, DatePicker, InputNumber, Switch, Button, Alert } from 'antd';
import { useRouter } from 'next/navigation';
import { SaveOutlined, RollbackOutlined } from '@ant-design/icons';
import moment from 'moment';

const { Title, Paragraph, Text, Link } = Typography;    

export default function EditContentPage({ params }) {
    const router = useRouter();
    const [taskData, setTaskData] = useState(null);
    const [taskLoading, setTaskLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [updateSuccess, setUpdateSuccess] = useState(false);
    const [form] = Form.useForm();
    const unwrappedParams = React.use(params);

    // Fetch task data
    useEffect(() => {
        const fetchTaskData = async () => {
            try {
                const response = await fetch("http://127.0.0.1:8000/api/tasks/" + unwrappedParams.id);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                setTaskData(data);
                
                // Initialize form with current values
                form.setFieldsValue({
                    end_time: data.end_time ? moment(data.end_time) : null,
                    max_contents: data.max_contents,
                    is_active: data.is_active
                });
            } catch (error) {
                console.error("Error fetching task:", error);
                message.error("Failed to load task information");
            } finally {
                setTaskLoading(false);
            }
        };
        fetchTaskData();
    }, [unwrappedParams.id, form]);

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

    const handleUpdateTask = async (values) => {
        setUpdating(true);
        setUpdateSuccess(false);
        
        try {
            // Format the date properly for the API
            const formattedValues = {
                end_time: values.end_time ? values.end_time.format('YYYY-MM-DD HH:mm:ss') : null,
                max_contents: values.max_contents,
                is_active: values.is_active
            };
            
            console.log('Sending data to API:', formattedValues); // Debug log
            
            const response = await fetch(`http://127.0.0.1:8000/api/tasks/${params.id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formattedValues),
            });

            console.log('API Response status:', response.status); // Debug log
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const updatedTask = await response.json();
            setTaskData(updatedTask);
            message.success("Task updated successfully!");
            setUpdateSuccess(true);
            
            // Update the form with the new values
            form.setFieldsValue({
                end_time: updatedTask.end_time ? moment(updatedTask.end_time) : null,
                max_contents: updatedTask.max_contents,
                is_active: updatedTask.is_active
            });
            
        } catch (error) {
            console.error("Error updating task:", error);
            message.error(`Failed to update task: ${error.message}`);
        } finally {
            setUpdating(false);
        }
    };

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
    
    const goBack = () => {
        router.push('/tasklist');
    };

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
            <Title level={2} style={{ color: '#1890ff', marginBottom: '24px' }}>
                Edit YouTube Monitoring Task
            </Title>

            {updateSuccess && (
                <Alert
                    message="Update Successful"
                    description="The task has been updated successfully."
                    type="success"
                    showIcon
                    closable
                    style={{ marginBottom: '20px' }}
                    afterClose={() => setUpdateSuccess(false)}
                />
            )}

            <Card
                title="Task Information"
                style={{ 
                    marginBottom: '30px',
                    boxShadow: '0px 5px 15px rgba(0, 0, 0, 0.1)',
                    borderRadius: '8px',
                }}
                loading={taskLoading}
                extra={
                    <Button icon={<RollbackOutlined />} onClick={goBack}>
                        Back to List
                    </Button>
                }
            >
                {taskData && (
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={handleUpdateTask}
                        initialValues={{
                            end_time: taskData.end_time ? moment(taskData.end_time) : null,
                            max_contents: taskData.max_contents,
                            is_active: taskData.is_active
                        }}
                    >
                        <Descriptions bordered column={1} size="middle">
                            <Descriptions.Item label="Content Category">
                                <a href={taskData.url} target="_blank" rel="noopener noreferrer">
                                    {taskData.category}
                                </a>
                            </Descriptions.Item>
                            <Descriptions.Item label="URL">{taskData.url}</Descriptions.Item>
                            <Descriptions.Item label="Scheduled Hours">{convertMinutesToHoursMinutes(taskData.scheduled_hours)}</Descriptions.Item>

                            {/* Editable field: End Time */}
                            <Descriptions.Item label="End Time">
                                <Form.Item 
                                    name="end_time"
                                    noStyle
                                >
                                    <DatePicker 
                                        showTime 
                                        format="YYYY-MM-DD HH:mm:ss"
                                        style={{ width: '100%' }}
                                    />
                                </Form.Item>
                            </Descriptions.Item>
                            
                            {/* Editable field: Max Videos */}
                            <Descriptions.Item label="Max Contents">
                                <Form.Item 
                                    name="max_contents"
                                    noStyle
                                >
                                    <InputNumber 
                                        min={1} 
                                        max={100}
                                        style={{ width: '100%' }}
                                    />
                                </Form.Item>
                            </Descriptions.Item>
                            
                            {/* Editable field: Status */}
                            <Descriptions.Item label="Status">
                                <Form.Item 
                                    name="is_active"
                                    noStyle
                                    valuePropName="checked"
                                >
                                    <Switch 
                                        checkedChildren="ACTIVE" 
                                        unCheckedChildren="INACTIVE"
                                    />
                                </Form.Item>
                            </Descriptions.Item>
                            
                            <Descriptions.Item label="Created At">{formatDate(taskData.created_at)}</Descriptions.Item>
                            <Descriptions.Item label="Updated At">{formatDate(taskData.updated_at)}</Descriptions.Item>
                            <Descriptions.Item label="Last Scraped At">{formatDate(taskData.last_scraped_at)}</Descriptions.Item>
                        </Descriptions>
                        
                        <div style={{ marginTop: '24px', textAlign: 'right' }}>
                            <Button 
                                type="primary" 
                                htmlType="submit"
                                loading={updating}
                                icon={<SaveOutlined />}
                                size="large"
                            >
                                Update Task
                            </Button>
                        </div>
                    </Form>
                )}
            </Card>
        </div>
    );
}