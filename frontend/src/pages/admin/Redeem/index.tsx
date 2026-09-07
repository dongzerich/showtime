import { useState } from 'react'
import {
  Card,
  Descriptions,
  Form,
  Input,
  Button,
  Space,
  Tag,
  message,
  Result,
} from 'antd'
import { ScanOutlined } from '@ant-design/icons'
import { redeemTicket, type TicketRedemption } from '../../../api/admin'

const ticketStatusMap: Record<string, { text: string; color: string }> = {
  UNUSED: { text: '未使用', color: 'default' },
  USED: { text: '已核销', color: 'success' },
  REFUNDING: { text: '退款中', color: 'processing' },
  REFUNDED: { text: '已退款', color: 'default' },
  EXCHANGING: { text: '换票中', color: 'warning' },
  EXCHANGED: { text: '已换票', color: 'default' },
}

const Redeem = () => {
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<TicketRedemption | null>(null)
  const [errorMsg, setErrorMsg] = useState('')

  const handleRedeem = async () => {
    try {
      const values = await form.validateFields()
      setSubmitting(true)
      setErrorMsg('')
      setResult(null)
      try {
        const res = await redeemTicket({
          qrCode: values.qrCode.trim(),
          checkDevice: values.checkDevice.trim() || 'admin-console',
        })
        if (res.error) {
          setErrorMsg(res.error.message || '核销失败')
          message.error('核销失败')
          return
        }
        if (res.data?.data) {
          const ticket = res.data.data
          setResult(ticket)
          const m = ticketStatusMap[ticket.ticketStatus]
          message.success(`核销成功：${ticket.eTicketNo}（${m ? m.text : ticket.ticketStatus}）`)
          form.setFieldValue('qrCode', '')
        } else {
          setErrorMsg('核销接口未返回数据')
          message.error('核销失败')
        }
      } catch {
        setErrorMsg('核销请求异常')
        message.error('核销请求异常')
      } finally {
        setSubmitting(false)
      }
    } catch {
      // 表单校验失败
    }
  }

  const renderResult = () => {
    if (errorMsg) {
      return (
        <Result
          status="error"
          title="核销失败"
          subTitle={errorMsg}
          style={{ padding: '24px 0' }}
        />
      )
    }
    if (!result) return null
    const m = ticketStatusMap[result.ticketStatus]
    return (
      <Card title="核销结果" style={{ marginTop: 16 }}>
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="电子票ID">{result.eTicketId}</Descriptions.Item>
          <Descriptions.Item label="电子票号">{result.eTicketNo}</Descriptions.Item>
          <Descriptions.Item label="订单ID">{result.orderId}</Descriptions.Item>
          <Descriptions.Item label="订单明细ID">{result.orderItemId}</Descriptions.Item>
          <Descriptions.Item label="场次ID">{result.sessionId}</Descriptions.Item>
          <Descriptions.Item label="票状态">
            <Tag color={m ? m.color : 'default'}>{m ? m.text : result.ticketStatus}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="核销时间">
            {result.checkTime ? new Date(result.checkTime).toLocaleString('zh-CN') : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="核销设备">{result.checkDevice}</Descriptions.Item>
          <Descriptions.Item label="核销人">{result.checkBy}</Descriptions.Item>
        </Descriptions>
      </Card>
    )
  }

  return (
    <div style={{ maxWidth: 680 }}>
      <Card title="电子票核销">
        <Form form={form} layout="vertical" onFinish={handleRedeem}>
          <Form.Item
            name="qrCode"
            label="电子票二维码内容"
            rules={[{ required: true, message: '请输入/扫码得到的电子票二维码内容' }]}
          >
            <Input
              placeholder="粘贴电子票二维码内容或票号"
              size="large"
              prefix={<ScanOutlined />}
              allowClear
            />
          </Form.Item>
          <Form.Item
            name="checkDevice"
            label="核销设备（选填，默认 admin-console）"
          >
            <Input placeholder="如：闸机01 / 检票口A" maxLength={50} />
          </Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={submitting} icon={<ScanOutlined />}>
              核销
            </Button>
          </Space>
        </Form>
      </Card>
      {renderResult()}
    </div>
  )
}

export default Redeem