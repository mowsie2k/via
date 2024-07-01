import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";

interface FormValues {
  title: string;
  description: string;
  author: string;
  category: string;
}

const KnowledgeBaseForm = () => {
  const initialValues: FormValues = {
    title: "",
    description: "",
    author: "",
    category: "",
  };

  const validationSchema = Yup.object({
    title: Yup.string().required("Required"),
    description: Yup.string().required("Required"),
    author: Yup.string().required("Required"),
    category: Yup.string().required("Required"),
  });

  const handleSubmit = async (
    values: FormValues,
    { setSubmitting }: { setSubmitting: (isSubmitting: boolean) => void }
  ) => {
    try {
      // Add your logic to create a Google Sheets document and upload it to Google Drive
      console.log("Form values:", values);
      // Reset form after submission
      setSubmitting(false);
    } catch (error) {
      console.error("Error submitting form:", error);
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Knowledge Base Form</h1>
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            <div className="mb-4">
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <Field
                type="text"
                name="title"
                id="title"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
              />
              <ErrorMessage name="title" component="div" className="text-red-500 text-sm" />
            </div>

            <div className="mb-4">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <Field
                as="textarea"
                name="description"
                id="description"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
              />
              <ErrorMessage name="description" component="div" className="text-red-500 text-sm" />
            </div>

            <div className="mb-4">
              <label htmlFor="author" className="block text-sm font-medium text-gray-700">
                Author
              </label>
              <Field
                type="text"
                name="author"
                id="author"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
              />
              <ErrorMessage name="author" component="div" className="text-red-500 text-sm" />
            </div>

            <div className="mb-4">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                Category
              </label>
              <Field
                type="text"
                name="category"
                id="category"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
              />
              <ErrorMessage name="category" component="div" className="text-red-500 text-sm" />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="bg-blue-500 text-white px-4 py-2 rounded-md"
            >
              Submit
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default KnowledgeBaseForm;
