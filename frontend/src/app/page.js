"use client";


import React, { useEffect, useState } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Checkbox, Form, Input, Card, Flex, message } from 'antd';
import { useRouter } from 'next/navigation';


export default function Home() {

    const router = useRouter();
    const [loading, setLoading] = useState(false);


    const onFinish = async(values) => {

        try {
            setLoading(true);
            
            // In a real app, you would call your API here
            await new Promise(resolve => setTimeout(resolve, 1000));

            if (values.username === 'admin' && values.password == 'adminpass'){
                message.success('Login successful!');
                localStorage.setItem('user', JSON.stringify({username: values.username}));
                router.push('/tasklist');
            }

            else {
                message.error("Invalid username or password. Please try again.");
            }

        } catch(error) {
            console.error("Login error:", error);
            message.error("An error occurred during login. Please try again later.");
        }

        finally {
            setLoading(false);
        }


    };







    return (


        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
            
                <h1 style={{ fontSize: '42px', marginBottom: '40px', textAlign: 'center', color: '#1890ff' }}>
                    YouTube Monitoring System
                </h1>
                
                <Card style={{ 
                    width: 500, 
                    padding: 20, 
                    boxShadow: '0px 10px 25px rgba(180, 255, 150, 0.67)',
                    borderRadius: '8px'
                }}>

                <div>

                    <h1 style={{ textAlign: "center", fontSize: '28px', marginBottom: '24px' }}>Login the System</h1>


                    <Form
                    name="login"
                    initialValues={{ remember: true }}
                    style={{ maxWidth: 460 }}
                    onFinish={onFinish}
                    size="large"
                    >
                    <Form.Item
                        name="username"
                        rules={[{ required: true, message: 'Please input your Username!' }]}
                    >
                        <Input prefix={<UserOutlined />} placeholder="Username" size="large" />
                    </Form.Item>
                    <Form.Item
                        name="password"
                        rules={[{ required: true, message: 'Please input your Password!' }]}
                    >
                        <Input prefix={<LockOutlined />} type="password" placeholder="Password" size="large" />
                    </Form.Item>



                    <Form.Item>
                        <Button block type="primary" htmlType="submit" size="large">
                        Log in
                        </Button>
                    </Form.Item>
                    </Form>



                </div>

            </Card>
        </div>
    );


}