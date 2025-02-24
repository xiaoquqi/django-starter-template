<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table';

import { Page } from '@vben/common-ui';

import { Button, message, Modal, Form, Input, Select, Spin } from 'ant-design-vue';

import { useVbenVxeGrid } from '#/adapter/vxe-table';

import { getPostListApi, createPostApi, getTagListApi, getCategoryListApi } from '#/api/sample';

import { ref, onMounted, onUnmounted, watch } from 'vue';

interface RowType {
  id: number;
  title: string;
  content: string;
  author: string;
  category: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

const gridOptions: VxeGridProps<RowType> = {
  checkboxConfig: {
    highlight: true,
    labelField: 'name',
  },
  columns: [
    { title: '序号', type: 'seq', width: 50 },
    { field: 'id', title: 'ID' },
    { field: 'title', title: '标题', showOverflow: true },
    { field: 'content', title: '内容', showOverflow: true },
    { field: 'author', title: '作者' },
    { field: 'category', title: '分类' },
    {
      field: 'tags',
      title: '标签',
      formatter: ({ cellValue }) => Array.isArray(cellValue) ? cellValue.join(', ') : cellValue
    },
    { field: 'created_at', title: '创建时间', sortable: true },
    { field: 'updated_at', title: '更新时间', sortable: true },
  ],
  keepSource: true,
  proxyConfig: {
    ajax: {
      query: async ({ page }) => {
        const response = await getPostListApi({
          page: page.currentPage,
          page_size: page.pageSize,
        });
        return response;
      },
    },
    response: {
      result: 'results',
      total: 'count'
    }
  },
  pagerConfig: {
    enabled: true,
    pageSize: 10,
    pageSizes: [10, 20, 50, 100],
  },
  sortConfig: {
    multiple: true,
  },
  toolbarConfig: {
    custom: true,
    export: true,
    // import: true,
    refresh: true,
    zoom: true,
  },
};

const gridEvents: VxeGridListeners<RowType> = {
  cellClick: ({ row }) => {
    message.info(`cell-click: ${row.title}`);
  },
};

const [Grid, gridApi] = useVbenVxeGrid({
  gridOptions,
});

const formRef = ref();
const visible = ref(false);
const loading = ref(false);
const submitting = ref(false);
const tagsOptions = ref<{ label: string; value: string }[]>([]);
const categoriesOptions = ref<{ label: string; value: string }[]>([]);

const initialValues = ref({
  title: '',
  content: '',
  tags: [],
  category: undefined,
});

// 重置表单状态
const resetForm = () => {
  formRef.value?.resetFields();
  submitting.value = false;
};

// 改进获取选项的错误处理
const fetchOptions = async () => {
  try {
    loading.value = true;
    const [tagsRes, categoriesRes] = await Promise.all([
      getTagListApi(),
      getCategoryListApi()
    ]);

    // 修改为直接使用名称作为值
    tagsOptions.value = tagsRes.map(t => ({ label: t.name, value: t.name })); // 使用名称作为value
    categoriesOptions.value = categoriesRes.map(c => ({ label: c.name, value: c.name })); // 使用名称作为value
  } catch (error) {
    message.error(`获取选项数据失败: ${error.message}`);
    console.error('Failed to fetch options:', error);
    tagsOptions.value = [];
    categoriesOptions.value = [];
  } finally {
    loading.value = false;
  }
};

// 修改表单提交处理
const handleSubmit = async () => {
  if (submitting.value) return;

  try {
    submitting.value = true;
    const values = await formRef.value?.validateFields();

    // 直接提交名称而不是ID
    await createPostApi({
      ...values,
      tags: values.tags || [],
      category: values.category, // 直接使用名称字符串
      author: 1,
    });

    message.success('创建成功');
    visible.value = false;
    resetForm();
    gridApi.value?.commitProxy('query');
  } catch (error) {
    if (error.isAxiosError) {
      message.error(error.response?.data?.message || '创建失败：网络错误');
    } else if (error.message) {
      message.error(error.message);
    } else {
      message.error('创建失败：表单验证错误');
    }
  } finally {
    submitting.value = false;
  }
};

// 监听弹窗关闭
watch(visible, (newVal) => {
  if (!newVal) {
    resetForm();
  }
});

// 组件卸载时清理
onUnmounted(() => {
  formRef.value?.resetFields();
});

onMounted(fetchOptions);
</script>

<template>
  <Page description="Sample表格示例，用于演示调用Django API获取数据后的数据展现。" title="Sample表格示例">
    <div class="mb-4">
    </div>

    <Grid table-title="Post列表" table-title-help="用于展现所有Post">
      <template #toolbar-tools>
        <Button class="mr-2" type="primary" @click="visible = true">
          新增
        </Button>
      </template>
    </Grid>

    <Modal
      v-model:visible="visible"
      title="新建文章"
      :confirmLoading="submitting"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <Spin :spinning="loading">
        <Form
          layout="vertical"
          :model="initialValues"
          ref="formRef"
          :rules="{
            title: [
              { required: true, message: '请输入标题' },
              { max: 100, message: '标题最多100个字符' }
            ],
            content: [
              { required: true, message: '请输入内容' },
              { max: 1000, message: '内容最多1000个字符' }
            ],
            tags: [
              {
                required: true,
                message: '请选择至少一个标签',
                type: 'array',
                min: 1
              }
            ],
            category: [
              { required: true, message: '请选择分类', type: 'string' }
            ]
          }"
        >
          <Form.Item label="标题" name="title">
            <Input v-model:value="initialValues.title" placeholder="请输入文章标题" />
          </Form.Item>
          <Form.Item label="内容" name="content">
            <Input.TextArea v-model:value="initialValues.content" placeholder="请输入文章内容" :rows="4" />
          </Form.Item>
          <Form.Item label="标签" name="tags">
            <Select
              v-model:value="initialValues.tags"
              mode="tags"
              placeholder="请选择或输入标签"
              :options="tagsOptions"
              :maxTagCount="2"
              :loading="loading"
              :disabled="loading"
              :fieldNames="{ label: 'label', value: 'value', options: 'options' }"
            />
          </Form.Item>
          <Form.Item label="分类" name="category">
            <Select
              v-model:value="initialValues.category"
              mode="combobox"
              placeholder="请选择或输入分类"
              :options="categoriesOptions"
              :loading="loading"
              :disabled="loading"
              :fieldNames="{ label: 'label', value: 'value' }"
            />
          </Form.Item>
          <div style="color: red">Debug: {{ initialValues }}</div>
        </Form>
      </Spin>
    </Modal>
  </Page>
</template>