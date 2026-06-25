import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authApi } from '@/api/auth'
import { registerSchema, type RegisterFormData } from '@/lib/validations'

export default function RegisterPage() {
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await authApi.register({
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      })

      toast.success('Регистрация успешна! Войдите в аккаунт.')
      navigate('/login')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Ошибка регистрации'
      toast.error(message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Tinder for Developers
            </h1>
            <p className="text-gray-600">
              Создайте аккаунт
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Full Name */}
            <div>
              <Label htmlFor="full_name">Имя</Label>
              <Input
                id="full_name"
                type="text"
                placeholder="Иван Иванов"
                autoComplete="name"
                error={errors.full_name?.message}
                {...register('full_name')}
              />
            </div>

            {/* Email */}
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                error={errors.email?.message}
                {...register('email')}
              />
            </div>

            {/* Password */}
            <div>
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                autoComplete="new-password"
                error={errors.password?.message}
                {...register('password')}
              />
            </div>

            {/* Confirm Password */}
            <div>
              <Label htmlFor="confirmPassword">Подтвердите пароль</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                autoComplete="new-password"
                error={errors.confirmPassword?.message}
                {...register('confirmPassword')}
              />
            </div>

            {/* Submit */}
            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={isSubmitting}
            >
              Зарегистрироваться
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Уже есть аккаунт?{' '}
              <Link
                to="/login"
                className="font-medium text-primary hover:text-primary/80"
              >
                Войти
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}