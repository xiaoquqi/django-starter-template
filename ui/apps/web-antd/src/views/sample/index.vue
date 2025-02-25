<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table';

import { Page } from '@vben/common-ui';

import {
  Button, message, Modal, Form, Input, Select, Spin,
} from 'ant-design-vue';

import { useVbenVxeGrid } from '#/adapter/vxe-table';

import {
  getPostListApi,
  createPostApi,
  getTagListApi,
  getCategoryListApi,
} from '#/api/sample';

import { ref, onMounted, onUnmounted, watch } from 'vue';

// Type definition for table row structure
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

// Grid configuration with proper type safety
const gridOptions: VxeGridProps<RowType> = {
  checkboxConfig: {
    highlight: true,
  },
  columns: [
    { title: 'Seq', type: 'seq', width: 50 },
    { field: 'id', title: 'ID' },
    { field: 'title', title: 'Title', showOverflow: true },
    { field: 'content', title: 'Content', showOverflow: true },
    { field: 'author', title: 'Author' },
    { field: 'category', title: 'Category' },
    {
      field: 'tags',
      title: 'Tags',
      formatter: ({ cellValue }) =>
        Array.isArray(cellValue) ? cellValue.join(', ') : cellValue
    },
    { field: 'created_at', title: 'Created At', sortable: true },
    { field: 'updated_at', title: 'Updated At', sortable: true },
  ],
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
  toolbarConfig: {
    custom: true,
    export: true,
    refresh: true,
    zoom: true,
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

// Reset form state when modal closes
const resetForm = () => {
  formRef.value?.resetFields();
  submitting.value = false;
};

// Fetch options with error handling and loading state
const fetchOptions = async () => {
  try {
    loading.value = true;
    // Parallel API calls for better performance
    const [tagsRes, categoriesRes] = await Promise.all([
      getTagListApi(),
      getCategoryListApi()
    ]);

    // Transform API response to Select options format
    tagsOptions.value = tagsRes.map(t =>
      ({ label: t.name, value: t.name }));
    categoriesOptions.value = categoriesRes.map(c =>
      ({ label: c.name, value: c.name }));
  } catch (error) {
    // Unified error handling for API failures
    message.error(`Failed to fetch options: ${error.message}`);
    console.error('API Error:', error);
    // Reset options to prevent stale data
    tagsOptions.value = [];
    categoriesOptions.value = [];
  } finally {
    loading.value = false;
  }
};

// Form submission handler with validation
const handleSubmit = async () => {
  if (submitting.value) return;

  try {
    submitting.value = true;
    const values = await formRef.value?.validateFields();

    // Submit form data directly using names instead of IDs
    // (Backend expects name strings for category/tags)
    await createPostApi({
      ...values,
      tags: values.tags || [],  // Ensure array type safety
      category: values.category,
      author: 1,  // Hardcoded for demo (should use actual auth system)
    });

    message.success('Post created successfully');
    visible.value = false;
    resetForm();
    // Refresh grid data after successful submission
    gridApi.value?.commitProxy('query');
  } catch (error) {
    // Handle different error types appropriately
    if (error.isAxiosError) {
      message.error(error.response?.data?.message || 'Network error');
    } else if (error.message) {
      message.error(error.message);
    } else {
      message.error('Form validation failed');
    }
  } finally {
    submitting.value = false;
  }
};

// Cleanup form state when component unmounts
onUnmounted(() => {
  formRef.value?.resetFields();
});

onMounted(fetchOptions);
</script>

<template>
  <Page
    description="Sample table demonstrating data presentation from Django API"
    title="Sample Table Demo"
  >

    <Grid table-title="Post List" table-title-help="Used to display all Posts">
      <template #toolbar-tools>
        <Button class="mr-2" type="primary" @click="visible = true">
          Add
        </Button>
      </template>
    </Grid>

    <Modal
      v-model:visible="visible"
      title="New Post"
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
              { required: true, message: 'Title is required' },
              { max: 100, message: 'Max 100 characters' }
            ],
            content: [
              { required: true, message: 'Content is required' },
              { max: 1000, message: 'Max 1000 characters' }
            ],
            tags: [
              {
                required: true,
                message: 'Please select at least one tag',
                type: 'array',
                min: 1
              }
            ],
            category: [
              { required: true, message: 'Please select a category', type: 'string' }
            ]
          }"
        >
          <Form.Item label="Title" name="title">
            <Input
              v-model:value="initialValues.title"
              placeholder="Enter post title"
            />
          </Form.Item>
          <Form.Item label="Content" name="content">
            <Input.TextArea
              v-model:value="initialValues.content"
              placeholder="Enter post content"
              :rows="4"
            />
          </Form.Item>
          <Form.Item label="Tags" name="tags">
            <Select
              v-model:value="initialValues.tags"
              mode="tags"
              placeholder="Select or enter tags"
              :options="tagsOptions"
              :maxTagCount="2"
              :loading="loading"
              :disabled="loading"
            />
          </Form.Item>
          <Form.Item label="Category" name="category">
            <Select
              v-model:value="initialValues.category"
              mode="combobox"
              placeholder="Select or enter category"
              :options="categoriesOptions"
              :loading="loading"
              :disabled="loading"
            />
          </Form.Item>
        </Form>
      </Spin>
    </Modal>
  </Page>
</template>