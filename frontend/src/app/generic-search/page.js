'use client';
import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Spin, Typography, Divider, Descriptions, Button, message, Row, Col, Input, Select, DatePicker, Form, Space } from 'antd';
import { useRouter } from 'next/navigation';
import { RollbackOutlined, LinkOutlined, UserOutlined, CalendarOutlined, EnvironmentOutlined, DownOutlined, UpOutlined, ExportOutlined, SearchOutlined, FilterOutlined, ClearOutlined } from '@ant-design/icons';
const { Title, Paragraph, Text, Link } = Typography;
const { RangePicker } = DatePicker;

export default function GenericSearch({ params }) {
    const router = useRouter();
    const [taskData, setTaskData] = useState(null);
    const [contentData, setContentData] = useState([]);
    const [filteredData, setFilteredData] = useState([]);
    const [taskLoading, setTaskLoading] = useState(true);
    const [contentLoading, setContentLoading] = useState(false);
    const [expandedCards, setExpandedCards] = useState(new Set()); // Track which cards are expanded

    const [searchForm] = Form.useForm();
    const [searchParams, setSearchParams] = useState({
        category:'',
        search: '',
        author: '',
        author_location: '',
        published_time_from: '',
        published_time_to: '',
        sort_by_published_time: ''
    })
    

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

    const fetchContentData = async (params = {}) => {
        setContentLoading(true)

        try {

            const queryParams = new URLSearchParams()
                
            Object.entries(params).forEach(([key, value]) => {
                if (value && value!== '')
                    queryParams.append(key, value)
            })

            const queryString = queryParams.toString()
            const url = `http://127.0.0.1:8000/api/tasks/elastic-search${queryString ? `?${queryString}` : ''}`
            console.log("Fetching contents from URL:", url); // Debug log



            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setContentData(data.articles || []);
            setFilteredData(data.articles || []);
        } catch (error) {
            console.error("Error fetching contents:", error);
            message.error("Failed to load video contents");
        } finally {
            setContentLoading(false);
        }
    };

    const hanadleSearch = (values) => {
        const params = {}
        if (values.category) params.category = values.category;
        if (values.search) params.search = values.search;
        if (values.author) params.author = values.author;
        if (values.author_location) params.author_location = values.author_location;
        if (values.dateRange && values.dateRange.length === 2){
            params.published_time_from = values.dateRange[0].format('YYYY-MM-DD HH:mm:ss+06:00')
            params.published_time_to = values.dateRange[1].format('YYYY-MM-DD HH:mm:ss+06:00')
        }
        if (values.sort_by_published_time) params.sort_by_published_time = values.sort_by_published_time
        
        setSearchParams(params)
        fetchContentData(params);

    }

    const handleClearFilters = () => {
        searchForm.resetFields()
        setSearchParams({})
        fetchContentData()
    }



    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    }

    const truncateText = (text, maxLength = 300) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    // Toggle expand/collapse for individual cards
    const toggleExpand = (index) => {
        const newExpandedCards = new Set(expandedCards);
        if (newExpandedCards.has(index)) {
            newExpandedCards.delete(index);
        } else {
            newExpandedCards.add(index);
        }
        setExpandedCards(newExpandedCards);
    }


    const goBack = () => {
        router.push('/tasklist');
    }



    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
            <Title level={2} style={{ color: '#1890ff', marginBottom: '24px' }}>
                Prothom Alo News Content
            </Title>
            

            <Card
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <FilterOutlined />
                        <span>Search & Filter Articles</span>
                    </div>
                }
                style={{
                    marginBottom: '30px',
                    boxShadow: '0px 5px 15px rgba(0, 0, 0, 0.1)',
                    borderRadius: '8px',
                }}
                extra={
                    <Button icon={<RollbackOutlined />} onClick={goBack} style={{ marginLeft: '8px' }}> Back to tasklist </Button>
                }   
            >

                <Form 
                    form={searchForm}
                    layout='vertical'
                    onFinish={hanadleSearch}
                    initialValues={{
                        sort_by_published_time: 'desc'
                    }}
                >

                    <Row gutter={[16, 16]}>

                        <Col xs={24} sm={12} md={8}>
                            <Form.Item
                                name="category"
                                label="Search Category"
                            >
                                <Select
                                    options={categoryOptions}
                                    placeholder="Select News Category"
                                    allowClear
                                    showSearch
                                    filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                            }
                                />
                            </Form.Item>
                        </Col>



                        <Col xs={24} sm={12} md={8}>
                            <Form.Item
                                name="search"
                                label="Search in Content"
                            >
                                <Input
                                    placeholder="e.g., বিরোধী পক্ষ"
                                    prefix={<SearchOutlined />}
                                    allowClear
                                />
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={8}>
                            <Form.Item
                                name="author"
                                label="Author"
                            >
                                <Input
                                    placeholder="e.g., জোবায়ের"
                                    prefix={<UserOutlined />}
                                    allowClear
                                />
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={8}>
                            <Form.Item
                                name="author_location"
                                label="Author Location"
                            >
                                <Input
                                    placeholder="e.g., ঢাকা"
                                    prefix={<EnvironmentOutlined />}
                                    allowClear
                                />
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={8}>
                            <Form.Item
                                name="dateRange"
                                label="Published Date Range"
                            >
                                <RangePicker
                                    showTime
                                    format="YYYY-MM-DD HH:mm"
                                    placeholder={['From Date', 'To Date']}
                                    style={{ width: '100%' }}
                                />
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={8}>
                            <Form.Item
                                name="sort_by_published_time"
                                label="Sort by Published Time"
                            >
                                <Select
                                    placeholder="Select sorting"
                                    options={[
                                        { label: 'Newest First', value: 'desc' },
                                        { label: 'Oldest First', value: 'asc' }
                                    ]}
                                />
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={8} style={{ display: 'flex', alignItems: 'end' }}>
                            <Space style={{ width: '100%' }}>
                                <Button 
                                    type="primary" 
                                    htmlType="submit" 
                                    icon={<SearchOutlined />}
                                    loading={contentLoading}
                                >
                                    Search
                                </Button>
                                <Button 
                                    onClick={handleClearFilters}
                                    icon={<ClearOutlined />}
                                >
                                    Clear
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Form>
            </Card>
                
            

            <Card
                title={
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Article Contents</span>
                        <Tag color="blue">Total: {contentData.length}</Tag>
                    </div>
                }
                style={{ 
                    boxShadow: '0px 5px 15px rgba(0, 0, 0, 0.1)',
                    borderRadius: '8px',
                }}
            >
                {contentLoading ? (
                    <div style={{ textAlign: 'center', padding: '50px' }}>
                        <Spin size="large" />
                        <div style={{ marginTop: '16px' }}>Loading articles...</div>
                    </div>
                ) : (
                    <Row gutter={[16, 16]}>
                        {contentData.map((article, index) => (
                            <Col xs={24} key={index}>
                                <Card
                                    size="small"
                                    style={{ 
                                        marginBottom: '16px',
                                        border: '1px solid #f0f0f0',
                                        borderRadius: '8px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                                    }}
                                >
                                    <div style={{ marginBottom: '12px' }}>
                                        <Title level={4} style={{ margin: '0 0 8px 0', color: '#1890ff' }}>
                                            <Link href={article.url} target="_blank">
                                                {article.inner_title || article.title} <ExportOutlined />
                                            </Link>
                                            
                                        </Title>
                                        
                                        <div style={{ 
                                            display: 'flex', 
                                            gap: '16px', 
                                            marginBottom: '12px',
                                            flexWrap: 'wrap',
                                            color: '#666'
                                        }}>
                                            <span>
                                                <UserOutlined style={{ marginRight: '4px' }} />
                                                {article.author || 'Unknown Author'}
                                            </span>
                                            {article.author_location && (
                                                <span>
                                                    <EnvironmentOutlined style={{ marginRight: '4px' }} />
                                                    {article.author_location}
                                                </span>
                                            )}
                                            <span>
                                                <CalendarOutlined style={{ marginRight: '4px' }} />
                                                {article.published_time_bn || formatDate(article.published_time)}
                                            </span>
                                        </div>
                                        
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Tag color="geekblue" style={{ marginBottom: '8px' }}>
                                                {article.category?.toUpperCase()}
                                            </Tag>
                                            {/* <Button 
                                                type="link" 
                                                size="small"
                                                icon={<LinkOutlined />}
                                                onClick={() => window.open(article.url, '_blank')}
                                                style={{ padding: '0' }}
                                            >
                                                Visit Original
                                            </Button> */}
                                        </div>
                                    </div>
                                    
                                    <Paragraph 
                                        style={{ 
                                            margin: 0,
                                            color: '#595959',
                                            lineHeight: '1.6'
                                        }}
                                    >
                                        {expandedCards.has(index) 
                                            ? article.main_story 
                                            : truncateText(article.main_story, 400)
                                        }
                                    </Paragraph>
                                    
                                    {article.main_story && article.main_story.length > 400 && (
                                        <div style={{ textAlign: 'center', marginTop: '12px' }}>
                                            <Button 
                                                type="link" 
                                                size="small"
                                                icon={expandedCards.has(index) ? <UpOutlined /> : <DownOutlined />}
                                                onClick={() => toggleExpand(index)}
                                                style={{ 
                                                    color: '#1890ff',
                                                    fontWeight: '500'
                                                }}
                                            >
                                                {expandedCards.has(index) ? 'Show Less' : 'Read More'}
                                            </Button>
                                        </div>
                                    )}
                                </Card>
                            </Col>
                        ))}
                        
                        {contentData.length === 0 && !contentLoading && (
                            <Col xs={24}>
                                <div style={{ 
                                    textAlign: 'center', 
                                    padding: '50px',
                                    color: '#999'
                                }}>
                                    <Text>No articles found for this task.</Text>
                                </div>
                            </Col>
                        )}
                    </Row>
                )}
            </Card>

        </div>
    );
}